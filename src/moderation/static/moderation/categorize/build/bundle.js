
(function(l, r) { if (!l || l.getElementById('livereloadscript')) return; r = l.createElement('script'); r.async = 1; r.src = '//' + (self.location.host || 'localhost').split(':')[0] + ':35729/livereload.js?snipver=1'; r.id = 'livereloadscript'; l.getElementsByTagName('head')[0].appendChild(r) })(self.document);
var app = (function () {
    'use strict';

    function noop() { }
    function run(fn) {
        return fn();
    }
    function blank_object() {
        return Object.create(null);
    }
    function run_all(fns) {
        fns.forEach(run);
    }
    function is_function(thing) {
        return typeof thing === 'function';
    }
    function safe_not_equal(a, b) {
        return a != a ? b == b : a !== b || ((a && typeof a === 'object') || typeof a === 'function');
    }
    function is_empty(obj) {
        return Object.keys(obj).length === 0;
    }

    // Track which nodes are claimed during hydration. Unclaimed nodes can then be removed from the DOM
    // at the end of hydration without touching the remaining nodes.
    let is_hydrating = false;
    function start_hydrating() {
        is_hydrating = true;
    }
    function end_hydrating() {
        is_hydrating = false;
    }
    function upper_bound(low, high, key, value) {
        // Return first index of value larger than input value in the range [low, high)
        while (low < high) {
            const mid = low + ((high - low) >> 1);
            if (key(mid) <= value) {
                low = mid + 1;
            }
            else {
                high = mid;
            }
        }
        return low;
    }
    function init_hydrate(target) {
        if (target.hydrate_init)
            return;
        target.hydrate_init = true;
        // We know that all children have claim_order values since the unclaimed have been detached
        const children = target.childNodes;
        /*
        * Reorder claimed children optimally.
        * We can reorder claimed children optimally by finding the longest subsequence of
        * nodes that are already claimed in order and only moving the rest. The longest
        * subsequence subsequence of nodes that are claimed in order can be found by
        * computing the longest increasing subsequence of .claim_order values.
        *
        * This algorithm is optimal in generating the least amount of reorder operations
        * possible.
        *
        * Proof:
        * We know that, given a set of reordering operations, the nodes that do not move
        * always form an increasing subsequence, since they do not move among each other
        * meaning that they must be already ordered among each other. Thus, the maximal
        * set of nodes that do not move form a longest increasing subsequence.
        */
        // Compute longest increasing subsequence
        // m: subsequence length j => index k of smallest value that ends an increasing subsequence of length j
        const m = new Int32Array(children.length + 1);
        // Predecessor indices + 1
        const p = new Int32Array(children.length);
        m[0] = -1;
        let longest = 0;
        for (let i = 0; i < children.length; i++) {
            const current = children[i].claim_order;
            // Find the largest subsequence length such that it ends in a value less than our current value
            // upper_bound returns first greater value, so we subtract one
            const seqLen = upper_bound(1, longest + 1, idx => children[m[idx]].claim_order, current) - 1;
            p[i] = m[seqLen] + 1;
            const newLen = seqLen + 1;
            // We can guarantee that current is the smallest value. Otherwise, we would have generated a longer sequence.
            m[newLen] = i;
            longest = Math.max(newLen, longest);
        }
        // The longest increasing subsequence of nodes (initially reversed)
        const lis = [];
        // The rest of the nodes, nodes that will be moved
        const toMove = [];
        let last = children.length - 1;
        for (let cur = m[longest] + 1; cur != 0; cur = p[cur - 1]) {
            lis.push(children[cur - 1]);
            for (; last >= cur; last--) {
                toMove.push(children[last]);
            }
            last--;
        }
        for (; last >= 0; last--) {
            toMove.push(children[last]);
        }
        lis.reverse();
        // We sort the nodes being moved to guarantee that their insertion order matches the claim order
        toMove.sort((a, b) => a.claim_order - b.claim_order);
        // Finally, we move the nodes
        for (let i = 0, j = 0; i < toMove.length; i++) {
            while (j < lis.length && toMove[i].claim_order >= lis[j].claim_order) {
                j++;
            }
            const anchor = j < lis.length ? lis[j] : null;
            target.insertBefore(toMove[i], anchor);
        }
    }
    function append(target, node) {
        if (is_hydrating) {
            init_hydrate(target);
            if ((target.actual_end_child === undefined) || ((target.actual_end_child !== null) && (target.actual_end_child.parentElement !== target))) {
                target.actual_end_child = target.firstChild;
            }
            if (node !== target.actual_end_child) {
                target.insertBefore(node, target.actual_end_child);
            }
            else {
                target.actual_end_child = node.nextSibling;
            }
        }
        else if (node.parentNode !== target) {
            target.appendChild(node);
        }
    }
    function insert(target, node, anchor) {
        if (is_hydrating && !anchor) {
            append(target, node);
        }
        else if (node.parentNode !== target || (anchor && node.nextSibling !== anchor)) {
            target.insertBefore(node, anchor || null);
        }
    }
    function detach(node) {
        node.parentNode.removeChild(node);
    }
    function destroy_each(iterations, detaching) {
        for (let i = 0; i < iterations.length; i += 1) {
            if (iterations[i])
                iterations[i].d(detaching);
        }
    }
    function element(name) {
        return document.createElement(name);
    }
    function text(data) {
        return document.createTextNode(data);
    }
    function space() {
        return text(' ');
    }
    function empty() {
        return text('');
    }
    function listen(node, event, handler, options) {
        node.addEventListener(event, handler, options);
        return () => node.removeEventListener(event, handler, options);
    }
    function prevent_default(fn) {
        return function (event) {
            event.preventDefault();
            // @ts-ignore
            return fn.call(this, event);
        };
    }
    function attr(node, attribute, value) {
        if (value == null)
            node.removeAttribute(attribute);
        else if (node.getAttribute(attribute) !== value)
            node.setAttribute(attribute, value);
    }
    function children(element) {
        return Array.from(element.childNodes);
    }
    function set_data(text, data) {
        data = '' + data;
        if (text.wholeText !== data)
            text.data = data;
    }
    function set_input_value(input, value) {
        input.value = value == null ? '' : value;
    }

    let current_component;
    function set_current_component(component) {
        current_component = component;
    }

    const dirty_components = [];
    const binding_callbacks = [];
    const render_callbacks = [];
    const flush_callbacks = [];
    const resolved_promise = Promise.resolve();
    let update_scheduled = false;
    function schedule_update() {
        if (!update_scheduled) {
            update_scheduled = true;
            resolved_promise.then(flush);
        }
    }
    function add_render_callback(fn) {
        render_callbacks.push(fn);
    }
    function add_flush_callback(fn) {
        flush_callbacks.push(fn);
    }
    let flushing = false;
    const seen_callbacks = new Set();
    function flush() {
        if (flushing)
            return;
        flushing = true;
        do {
            // first, call beforeUpdate functions
            // and update components
            for (let i = 0; i < dirty_components.length; i += 1) {
                const component = dirty_components[i];
                set_current_component(component);
                update(component.$$);
            }
            set_current_component(null);
            dirty_components.length = 0;
            while (binding_callbacks.length)
                binding_callbacks.pop()();
            // then, once components are updated, call
            // afterUpdate functions. This may cause
            // subsequent updates...
            for (let i = 0; i < render_callbacks.length; i += 1) {
                const callback = render_callbacks[i];
                if (!seen_callbacks.has(callback)) {
                    // ...so guard against infinite loops
                    seen_callbacks.add(callback);
                    callback();
                }
            }
            render_callbacks.length = 0;
        } while (dirty_components.length);
        while (flush_callbacks.length) {
            flush_callbacks.pop()();
        }
        update_scheduled = false;
        flushing = false;
        seen_callbacks.clear();
    }
    function update($$) {
        if ($$.fragment !== null) {
            $$.update();
            run_all($$.before_update);
            const dirty = $$.dirty;
            $$.dirty = [-1];
            $$.fragment && $$.fragment.p($$.ctx, dirty);
            $$.after_update.forEach(add_render_callback);
        }
    }
    const outroing = new Set();
    let outros;
    function group_outros() {
        outros = {
            r: 0,
            c: [],
            p: outros // parent group
        };
    }
    function check_outros() {
        if (!outros.r) {
            run_all(outros.c);
        }
        outros = outros.p;
    }
    function transition_in(block, local) {
        if (block && block.i) {
            outroing.delete(block);
            block.i(local);
        }
    }
    function transition_out(block, local, detach, callback) {
        if (block && block.o) {
            if (outroing.has(block))
                return;
            outroing.add(block);
            outros.c.push(() => {
                outroing.delete(block);
                if (callback) {
                    if (detach)
                        block.d(1);
                    callback();
                }
            });
            block.o(local);
        }
    }

    function destroy_block(block, lookup) {
        block.d(1);
        lookup.delete(block.key);
    }
    function update_keyed_each(old_blocks, dirty, get_key, dynamic, ctx, list, lookup, node, destroy, create_each_block, next, get_context) {
        let o = old_blocks.length;
        let n = list.length;
        let i = o;
        const old_indexes = {};
        while (i--)
            old_indexes[old_blocks[i].key] = i;
        const new_blocks = [];
        const new_lookup = new Map();
        const deltas = new Map();
        i = n;
        while (i--) {
            const child_ctx = get_context(ctx, list, i);
            const key = get_key(child_ctx);
            let block = lookup.get(key);
            if (!block) {
                block = create_each_block(key, child_ctx);
                block.c();
            }
            else if (dynamic) {
                block.p(child_ctx, dirty);
            }
            new_lookup.set(key, new_blocks[i] = block);
            if (key in old_indexes)
                deltas.set(key, Math.abs(i - old_indexes[key]));
        }
        const will_move = new Set();
        const did_move = new Set();
        function insert(block) {
            transition_in(block, 1);
            block.m(node, next);
            lookup.set(block.key, block);
            next = block.first;
            n--;
        }
        while (o && n) {
            const new_block = new_blocks[n - 1];
            const old_block = old_blocks[o - 1];
            const new_key = new_block.key;
            const old_key = old_block.key;
            if (new_block === old_block) {
                // do nothing
                next = new_block.first;
                o--;
                n--;
            }
            else if (!new_lookup.has(old_key)) {
                // remove old block
                destroy(old_block, lookup);
                o--;
            }
            else if (!lookup.has(new_key) || will_move.has(new_key)) {
                insert(new_block);
            }
            else if (did_move.has(old_key)) {
                o--;
            }
            else if (deltas.get(new_key) > deltas.get(old_key)) {
                did_move.add(new_key);
                insert(new_block);
            }
            else {
                will_move.add(old_key);
                o--;
            }
        }
        while (o--) {
            const old_block = old_blocks[o];
            if (!new_lookup.has(old_block.key))
                destroy(old_block, lookup);
        }
        while (n)
            insert(new_blocks[n - 1]);
        return new_blocks;
    }

    function bind(component, name, callback) {
        const index = component.$$.props[name];
        if (index !== undefined) {
            component.$$.bound[index] = callback;
            callback(component.$$.ctx[index]);
        }
    }
    function create_component(block) {
        block && block.c();
    }
    function mount_component(component, target, anchor, customElement) {
        const { fragment, on_mount, on_destroy, after_update } = component.$$;
        fragment && fragment.m(target, anchor);
        if (!customElement) {
            // onMount happens before the initial afterUpdate
            add_render_callback(() => {
                const new_on_destroy = on_mount.map(run).filter(is_function);
                if (on_destroy) {
                    on_destroy.push(...new_on_destroy);
                }
                else {
                    // Edge case - component was destroyed immediately,
                    // most likely as a result of a binding initialising
                    run_all(new_on_destroy);
                }
                component.$$.on_mount = [];
            });
        }
        after_update.forEach(add_render_callback);
    }
    function destroy_component(component, detaching) {
        const $$ = component.$$;
        if ($$.fragment !== null) {
            run_all($$.on_destroy);
            $$.fragment && $$.fragment.d(detaching);
            // TODO null out other refs, including component.$$ (but need to
            // preserve final state?)
            $$.on_destroy = $$.fragment = null;
            $$.ctx = [];
        }
    }
    function make_dirty(component, i) {
        if (component.$$.dirty[0] === -1) {
            dirty_components.push(component);
            schedule_update();
            component.$$.dirty.fill(0);
        }
        component.$$.dirty[(i / 31) | 0] |= (1 << (i % 31));
    }
    function init(component, options, instance, create_fragment, not_equal, props, dirty = [-1]) {
        const parent_component = current_component;
        set_current_component(component);
        const $$ = component.$$ = {
            fragment: null,
            ctx: null,
            // state
            props,
            update: noop,
            not_equal,
            bound: blank_object(),
            // lifecycle
            on_mount: [],
            on_destroy: [],
            on_disconnect: [],
            before_update: [],
            after_update: [],
            context: new Map(parent_component ? parent_component.$$.context : options.context || []),
            // everything else
            callbacks: blank_object(),
            dirty,
            skip_bound: false
        };
        let ready = false;
        $$.ctx = instance
            ? instance(component, options.props || {}, (i, ret, ...rest) => {
                const value = rest.length ? rest[0] : ret;
                if ($$.ctx && not_equal($$.ctx[i], $$.ctx[i] = value)) {
                    if (!$$.skip_bound && $$.bound[i])
                        $$.bound[i](value);
                    if (ready)
                        make_dirty(component, i);
                }
                return ret;
            })
            : [];
        $$.update();
        ready = true;
        run_all($$.before_update);
        // `false` as a special case of no DOM component
        $$.fragment = create_fragment ? create_fragment($$.ctx) : false;
        if (options.target) {
            if (options.hydrate) {
                start_hydrating();
                const nodes = children(options.target);
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                $$.fragment && $$.fragment.l(nodes);
                nodes.forEach(detach);
            }
            else {
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                $$.fragment && $$.fragment.c();
            }
            if (options.intro)
                transition_in(component.$$.fragment);
            mount_component(component, options.target, options.anchor, options.customElement);
            end_hydrating();
            flush();
        }
        set_current_component(parent_component);
    }
    /**
     * Base class for Svelte components. Used when dev=false.
     */
    class SvelteComponent {
        $destroy() {
            destroy_component(this, 1);
            this.$destroy = noop;
        }
        $on(type, callback) {
            const callbacks = (this.$$.callbacks[type] || (this.$$.callbacks[type] = []));
            callbacks.push(callback);
            return () => {
                const index = callbacks.indexOf(callback);
                if (index !== -1)
                    callbacks.splice(index, 1);
            };
        }
        $set($$props) {
            if (this.$$set && !is_empty($$props)) {
                this.$$.skip_bound = true;
                this.$$set($$props);
                this.$$.skip_bound = false;
            }
        }
    }

    /* src/CreateSocialUser.svelte generated by Svelte v3.38.3 */

    function create_fragment$2(ctx) {
    	let button;
    	let t0;
    	let t1;
    	let t2;
    	let button_disabled_value;
    	let mounted;
    	let dispose;

    	return {
    		c() {
    			button = element("button");
    			t0 = text("Create @");
    			t1 = text(/*screenName*/ ctx[0]);
    			t2 = text(" SocialUser");
    			button.disabled = button_disabled_value = !/*screenName*/ ctx[0];
    		},
    		m(target, anchor) {
    			insert(target, button, anchor);
    			append(button, t0);
    			append(button, t1);
    			append(button, t2);

    			if (!mounted) {
    				dispose = listen(button, "click", /*fetchApi*/ ctx[1]);
    				mounted = true;
    			}
    		},
    		p(ctx, [dirty]) {
    			if (dirty & /*screenName*/ 1) set_data(t1, /*screenName*/ ctx[0]);

    			if (dirty & /*screenName*/ 1 && button_disabled_value !== (button_disabled_value = !/*screenName*/ ctx[0])) {
    				button.disabled = button_disabled_value;
    			}
    		},
    		i: noop,
    		o: noop,
    		d(detaching) {
    			if (detaching) detach(button);
    			mounted = false;
    			dispose();
    		}
    	};
    }

    let devUrl = "https://local.doctoctoc.net";
    let createSocialUserPath = "/moderation/api/create-twitter-socialuser/";

    function instance$1($$self, $$props, $$invalidate) {
    	let { screenName } = $$props;

    	function getApiUrl() {
    		if (window.location.hostname == "localhost") {
    			return devUrl + createSocialUserPath + screenName + "/";
    		} else {
    			return createSocialUserPath + screenName + "/";
    		}
    	}

    	async function fetchApi() {
    		let url = getApiUrl();

    		//console.log(url);
    		await fetch(url).then(r => console.log(r));
    	}

    	

    	$$self.$$set = $$props => {
    		if ("screenName" in $$props) $$invalidate(0, screenName = $$props.screenName);
    	};

    	return [screenName, fetchApi];
    }

    class CreateSocialUser extends SvelteComponent {
    	constructor(options) {
    		super();
    		init(this, options, instance$1, create_fragment$2, safe_not_equal, { screenName: 0 });
    	}
    }

    /* src/UserName.svelte generated by Svelte v3.38.3 */

    function get_each_context(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[8] = list[i];
    	return child_ctx;
    }

    function get_each_context_1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[11] = list[i];
    	return child_ctx;
    }

    // (52:24) 
    function create_if_block_1(ctx) {
    	let each_blocks = [];
    	let each_1_lookup = new Map();
    	let each_1_anchor;
    	let each_value = /*socialusers*/ ctx[2];
    	const get_key = ctx => /*socialuser*/ ctx[8].id;

    	for (let i = 0; i < each_value.length; i += 1) {
    		let child_ctx = get_each_context(ctx, each_value, i);
    		let key = get_key(child_ctx);
    		each_1_lookup.set(key, each_blocks[i] = create_each_block(key, child_ctx));
    	}

    	return {
    		c() {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			each_1_anchor = empty();
    		},
    		m(target, anchor) {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(target, anchor);
    			}

    			insert(target, each_1_anchor, anchor);
    		},
    		p(ctx, dirty) {
    			if (dirty & /*socialusers, getBaseUrl*/ 4) {
    				each_value = /*socialusers*/ ctx[2];
    				each_blocks = update_keyed_each(each_blocks, dirty, get_key, 1, ctx, each_value, each_1_lookup, each_1_anchor.parentNode, destroy_block, create_each_block, each_1_anchor, get_each_context);
    			}
    		},
    		i: noop,
    		o: noop,
    		d(detaching) {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].d(detaching);
    			}

    			if (detaching) detach(each_1_anchor);
    		}
    	};
    }

    // (49:2) {#if socialusers && socialusers.length == 0 && screenName}
    function create_if_block(ctx) {
    	let p;
    	let t1;
    	let createsocialuser;
    	let updating_screenName;
    	let current;

    	function createsocialuser_screenName_binding(value) {
    		/*createsocialuser_screenName_binding*/ ctx[5](value);
    	}

    	let createsocialuser_props = {};

    	if (/*screenName*/ ctx[1] !== void 0) {
    		createsocialuser_props.screenName = /*screenName*/ ctx[1];
    	}

    	createsocialuser = new CreateSocialUser({ props: createsocialuser_props });
    	binding_callbacks.push(() => bind(createsocialuser, "screenName", createsocialuser_screenName_binding));

    	return {
    		c() {
    			p = element("p");
    			p.textContent = "Utilisateur inconnu dans notre base de données.";
    			t1 = space();
    			create_component(createsocialuser.$$.fragment);
    		},
    		m(target, anchor) {
    			insert(target, p, anchor);
    			insert(target, t1, anchor);
    			mount_component(createsocialuser, target, anchor);
    			current = true;
    		},
    		p(ctx, dirty) {
    			const createsocialuser_changes = {};

    			if (!updating_screenName && dirty & /*screenName*/ 2) {
    				updating_screenName = true;
    				createsocialuser_changes.screenName = /*screenName*/ ctx[1];
    				add_flush_callback(() => updating_screenName = false);
    			}

    			createsocialuser.$set(createsocialuser_changes);
    		},
    		i(local) {
    			if (current) return;
    			transition_in(createsocialuser.$$.fragment, local);
    			current = true;
    		},
    		o(local) {
    			transition_out(createsocialuser.$$.fragment, local);
    			current = false;
    		},
    		d(detaching) {
    			if (detaching) detach(p);
    			if (detaching) detach(t1);
    			destroy_component(createsocialuser, detaching);
    		}
    	};
    }

    // (65:8) {#each socialuser.category as cat}
    function create_each_block_1(ctx) {
    	let li;
    	let t_value = /*cat*/ ctx[11].label + "";
    	let t;

    	return {
    		c() {
    			li = element("li");
    			t = text(t_value);
    		},
    		m(target, anchor) {
    			insert(target, li, anchor);
    			append(li, t);
    		},
    		p(ctx, dirty) {
    			if (dirty & /*socialusers*/ 4 && t_value !== (t_value = /*cat*/ ctx[11].label + "")) set_data(t, t_value);
    		},
    		d(detaching) {
    			if (detaching) detach(li);
    		}
    	};
    }

    // (53:4) {#each socialusers as socialuser (socialuser.id) }
    function create_each_block(key_1, ctx) {
    	let div1;
    	let ul1;
    	let li0;
    	let a0;
    	let t0;
    	let a0_href_value;
    	let t1;
    	let li1;
    	let t2;
    	let t3_value = /*socialuser*/ ctx[8].id + "";
    	let t3;
    	let t4;
    	let li2;
    	let a1;
    	let t5;
    	let a1_href_value;
    	let t6;
    	let li3;
    	let t7;
    	let t8_value = /*socialuser*/ ctx[8].user_id + "";
    	let t8;
    	let t9;
    	let li4;
    	let t10;
    	let t11_value = /*socialuser*/ ctx[8].profile.json.screen_name + "";
    	let t11;
    	let t12;
    	let li5;
    	let t13;
    	let t14_value = /*socialuser*/ ctx[8].profile.json.name + "";
    	let t14;
    	let t15;
    	let li6;
    	let t16;
    	let div0;
    	let ul0;
    	let t17;
    	let each_value_1 = /*socialuser*/ ctx[8].category;
    	let each_blocks = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks[i] = create_each_block_1(get_each_context_1(ctx, each_value_1, i));
    	}

    	return {
    		key: key_1,
    		first: null,
    		c() {
    			div1 = element("div");
    			ul1 = element("ul");
    			li0 = element("li");
    			a0 = element("a");
    			t0 = text("🔗 SocialUser admin");
    			t1 = space();
    			li1 = element("li");
    			t2 = text("SocialUser id: ");
    			t3 = text(t3_value);
    			t4 = space();
    			li2 = element("li");
    			a1 = element("a");
    			t5 = text("🔗 Twitter profile");
    			t6 = space();
    			li3 = element("li");
    			t7 = text("Twitter user id: ");
    			t8 = text(t8_value);
    			t9 = space();
    			li4 = element("li");
    			t10 = text("Twitter screen name: ");
    			t11 = text(t11_value);
    			t12 = space();
    			li5 = element("li");
    			t13 = text("Twitter name: ");
    			t14 = text(t14_value);
    			t15 = space();
    			li6 = element("li");
    			t16 = text("category:\n        ");
    			div0 = element("div");
    			ul0 = element("ul");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			t17 = space();
    			attr(a0, "href", a0_href_value = "" + (getBaseUrl() + "/admin/moderation/socialuser/" + /*socialuser*/ ctx[8].id + "/change/"));
    			attr(a1, "href", a1_href_value = "https://twitter.com/intent/user?user_id=" + /*socialuser*/ ctx[8].profile.json.id_str);
    			attr(ul0, "class", "svelte-xis9q2");
    			attr(div0, "class", "parent svelte-xis9q2");
    			attr(ul1, "class", "svelte-xis9q2");
    			attr(div1, "class", "parent svelte-xis9q2");
    			this.first = div1;
    		},
    		m(target, anchor) {
    			insert(target, div1, anchor);
    			append(div1, ul1);
    			append(ul1, li0);
    			append(li0, a0);
    			append(a0, t0);
    			append(li0, t1);
    			append(ul1, li1);
    			append(li1, t2);
    			append(li1, t3);
    			append(ul1, t4);
    			append(ul1, li2);
    			append(li2, a1);
    			append(a1, t5);
    			append(ul1, t6);
    			append(ul1, li3);
    			append(li3, t7);
    			append(li3, t8);
    			append(ul1, t9);
    			append(ul1, li4);
    			append(li4, t10);
    			append(li4, t11);
    			append(ul1, t12);
    			append(ul1, li5);
    			append(li5, t13);
    			append(li5, t14);
    			append(ul1, t15);
    			append(ul1, li6);
    			append(li6, t16);
    			append(li6, div0);
    			append(div0, ul0);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(ul0, null);
    			}

    			append(div1, t17);
    		},
    		p(new_ctx, dirty) {
    			ctx = new_ctx;

    			if (dirty & /*socialusers*/ 4 && a0_href_value !== (a0_href_value = "" + (getBaseUrl() + "/admin/moderation/socialuser/" + /*socialuser*/ ctx[8].id + "/change/"))) {
    				attr(a0, "href", a0_href_value);
    			}

    			if (dirty & /*socialusers*/ 4 && t3_value !== (t3_value = /*socialuser*/ ctx[8].id + "")) set_data(t3, t3_value);

    			if (dirty & /*socialusers*/ 4 && a1_href_value !== (a1_href_value = "https://twitter.com/intent/user?user_id=" + /*socialuser*/ ctx[8].profile.json.id_str)) {
    				attr(a1, "href", a1_href_value);
    			}

    			if (dirty & /*socialusers*/ 4 && t8_value !== (t8_value = /*socialuser*/ ctx[8].user_id + "")) set_data(t8, t8_value);
    			if (dirty & /*socialusers*/ 4 && t11_value !== (t11_value = /*socialuser*/ ctx[8].profile.json.screen_name + "")) set_data(t11, t11_value);
    			if (dirty & /*socialusers*/ 4 && t14_value !== (t14_value = /*socialuser*/ ctx[8].profile.json.name + "")) set_data(t14, t14_value);

    			if (dirty & /*socialusers*/ 4) {
    				each_value_1 = /*socialuser*/ ctx[8].category;
    				let i;

    				for (i = 0; i < each_value_1.length; i += 1) {
    					const child_ctx = get_each_context_1(ctx, each_value_1, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_1(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(ul0, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value_1.length;
    			}
    		},
    		d(detaching) {
    			if (detaching) detach(div1);
    			destroy_each(each_blocks, detaching);
    		}
    	};
    }

    // (48:2) {#key socialusers}
    function create_key_block(ctx) {
    	let current_block_type_index;
    	let if_block;
    	let if_block_anchor;
    	let current;
    	const if_block_creators = [create_if_block, create_if_block_1];
    	const if_blocks = [];

    	function select_block_type(ctx, dirty) {
    		if (/*socialusers*/ ctx[2] && /*socialusers*/ ctx[2].length == 0 && /*screenName*/ ctx[1]) return 0;
    		if (/*socialusers*/ ctx[2]) return 1;
    		return -1;
    	}

    	if (~(current_block_type_index = select_block_type(ctx))) {
    		if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);
    	}

    	return {
    		c() {
    			if (if_block) if_block.c();
    			if_block_anchor = empty();
    		},
    		m(target, anchor) {
    			if (~current_block_type_index) {
    				if_blocks[current_block_type_index].m(target, anchor);
    			}

    			insert(target, if_block_anchor, anchor);
    			current = true;
    		},
    		p(ctx, dirty) {
    			let previous_block_index = current_block_type_index;
    			current_block_type_index = select_block_type(ctx);

    			if (current_block_type_index === previous_block_index) {
    				if (~current_block_type_index) {
    					if_blocks[current_block_type_index].p(ctx, dirty);
    				}
    			} else {
    				if (if_block) {
    					group_outros();

    					transition_out(if_blocks[previous_block_index], 1, 1, () => {
    						if_blocks[previous_block_index] = null;
    					});

    					check_outros();
    				}

    				if (~current_block_type_index) {
    					if_block = if_blocks[current_block_type_index];

    					if (!if_block) {
    						if_block = if_blocks[current_block_type_index] = if_block_creators[current_block_type_index](ctx);
    						if_block.c();
    					} else {
    						if_block.p(ctx, dirty);
    					}

    					transition_in(if_block, 1);
    					if_block.m(if_block_anchor.parentNode, if_block_anchor);
    				} else {
    					if_block = null;
    				}
    			}
    		},
    		i(local) {
    			if (current) return;
    			transition_in(if_block);
    			current = true;
    		},
    		o(local) {
    			transition_out(if_block);
    			current = false;
    		},
    		d(detaching) {
    			if (~current_block_type_index) {
    				if_blocks[current_block_type_index].d(detaching);
    			}

    			if (detaching) detach(if_block_anchor);
    		}
    	};
    }

    function create_fragment$1(ctx) {
    	let form;
    	let label;
    	let t1;
    	let input_1;
    	let t2;
    	let button;
    	let t3;
    	let button_disabled_value;
    	let t4;
    	let previous_key = /*socialusers*/ ctx[2];
    	let key_block_anchor;
    	let current;
    	let mounted;
    	let dispose;
    	let key_block = create_key_block(ctx);

    	return {
    		c() {
    			form = element("form");
    			label = element("label");
    			label.textContent = "Enter Twitter screen_name";
    			t1 = space();
    			input_1 = element("input");
    			t2 = space();
    			button = element("button");
    			t3 = text("Fetch!");
    			t4 = space();
    			key_block.c();
    			key_block_anchor = empty();
    			attr(label, "for", "screen_name");
    			attr(input_1, "type", "text");
    			attr(input_1, "name", "screen_name");
    			attr(input_1, "id", "screen_name");
    			attr(button, "type", "submit");
    			button.disabled = button_disabled_value = !/*input*/ ctx[0];
    			attr(form, "action", "");
    			attr(form, "method", "get");
    		},
    		m(target, anchor) {
    			insert(target, form, anchor);
    			append(form, label);
    			append(form, t1);
    			append(form, input_1);
    			set_input_value(input_1, /*input*/ ctx[0]);
    			append(form, t2);
    			append(form, button);
    			append(button, t3);
    			insert(target, t4, anchor);
    			key_block.m(target, anchor);
    			insert(target, key_block_anchor, anchor);
    			current = true;

    			if (!mounted) {
    				dispose = [
    					listen(input_1, "input", /*input_1_input_handler*/ ctx[4]),
    					listen(button, "click", function () {
    						if (is_function(/*onClickFetchApi*/ ctx[3](/*input*/ ctx[0]))) /*onClickFetchApi*/ ctx[3](/*input*/ ctx[0]).apply(this, arguments);
    					}),
    					listen(form, "submit", prevent_default(function () {
    						if (is_function(/*onClickFetchApi*/ ctx[3](/*input*/ ctx[0]))) /*onClickFetchApi*/ ctx[3](/*input*/ ctx[0]).apply(this, arguments);
    					}))
    				];

    				mounted = true;
    			}
    		},
    		p(new_ctx, [dirty]) {
    			ctx = new_ctx;

    			if (dirty & /*input*/ 1 && input_1.value !== /*input*/ ctx[0]) {
    				set_input_value(input_1, /*input*/ ctx[0]);
    			}

    			if (!current || dirty & /*input*/ 1 && button_disabled_value !== (button_disabled_value = !/*input*/ ctx[0])) {
    				button.disabled = button_disabled_value;
    			}

    			if (dirty & /*socialusers*/ 4 && safe_not_equal(previous_key, previous_key = /*socialusers*/ ctx[2])) {
    				group_outros();
    				transition_out(key_block, 1, 1, noop);
    				check_outros();
    				key_block = create_key_block(ctx);
    				key_block.c();
    				transition_in(key_block);
    				key_block.m(key_block_anchor.parentNode, key_block_anchor);
    			} else {
    				key_block.p(ctx, dirty);
    			}
    		},
    		i(local) {
    			if (current) return;
    			transition_in(key_block);
    			current = true;
    		},
    		o(local) {
    			transition_out(key_block);
    			current = false;
    		},
    		d(detaching) {
    			if (detaching) detach(form);
    			if (detaching) detach(t4);
    			if (detaching) detach(key_block_anchor);
    			key_block.d(detaching);
    			mounted = false;
    			run_all(dispose);
    		}
    	};
    }

    let apiProtocolDomain = "https://local.doctoctoc.net";
    let apiPath = "/moderation/api/socialuser/";

    function getBaseUrl() {
    	if (window.location.hostname == "localhost") {
    		return apiProtocolDomain;
    	} else {
    		return "";
    	}
    }

    function instance($$self, $$props, $$invalidate) {
    	let input = "";
    	let screenName = "";
    	let socialusers = null;

    	async function fetchApi() {
    		let url = getBaseUrl() + apiPath + "?search=" + screenName;
    		console.log(url);

    		await fetch(url).then(r => r.json()).then(data => {
    			//console.log(data);
    			$$invalidate(2, socialusers = data);
    		});

    		return socialusers;
    	}

    	

    	async function onClickFetchApi(input) {
    		if (input.startsWith("@")) {
    			$$invalidate(1, screenName = input.slice(1));
    		} else {
    			$$invalidate(1, screenName = input);
    		}

    		$$invalidate(2, socialusers = await fetchApi());
    	}

    	function input_1_input_handler() {
    		input = this.value;
    		$$invalidate(0, input);
    	}

    	function createsocialuser_screenName_binding(value) {
    		screenName = value;
    		$$invalidate(1, screenName);
    	}

    	return [
    		input,
    		screenName,
    		socialusers,
    		onClickFetchApi,
    		input_1_input_handler,
    		createsocialuser_screenName_binding
    	];
    }

    class UserName extends SvelteComponent {
    	constructor(options) {
    		super();
    		init(this, options, instance, create_fragment$1, safe_not_equal, {});
    	}
    }

    /* src/App.svelte generated by Svelte v3.38.3 */

    function create_fragment(ctx) {
    	let main;
    	let h2;
    	let t1;
    	let username;
    	let current;
    	username = new UserName({});

    	return {
    		c() {
    			main = element("main");
    			h2 = element("h2");
    			h2.textContent = "SocialUser";
    			t1 = space();
    			create_component(username.$$.fragment);
    			attr(main, "class", "svelte-1knh9dm");
    		},
    		m(target, anchor) {
    			insert(target, main, anchor);
    			append(main, h2);
    			append(main, t1);
    			mount_component(username, main, null);
    			current = true;
    		},
    		p: noop,
    		i(local) {
    			if (current) return;
    			transition_in(username.$$.fragment, local);
    			current = true;
    		},
    		o(local) {
    			transition_out(username.$$.fragment, local);
    			current = false;
    		},
    		d(detaching) {
    			if (detaching) detach(main);
    			destroy_component(username);
    		}
    	};
    }

    class App extends SvelteComponent {
    	constructor(options) {
    		super();
    		init(this, options, null, create_fragment, safe_not_equal, {});
    	}
    }

    return App;

}());
//# sourceMappingURL=bundle.js.map
