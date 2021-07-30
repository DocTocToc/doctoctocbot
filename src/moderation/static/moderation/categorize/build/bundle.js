
(function(l, r) { if (!l || l.getElementById('livereloadscript')) return; r = l.createElement('script'); r.async = 1; r.src = '//' + (self.location.host || 'localhost').split(':')[0] + ':35729/livereload.js?snipver=1'; r.id = 'livereloadscript'; l.getElementsByTagName('head')[0].appendChild(r) })(self.document);
var app = (function () {
    'use strict';

    function noop() { }
    function is_promise(value) {
        return value && typeof value === 'object' && typeof value.then === 'function';
    }
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
    function get_current_component() {
        if (!current_component)
            throw new Error('Function called outside component initialization');
        return current_component;
    }
    function onMount(fn) {
        get_current_component().$$.on_mount.push(fn);
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

    function handle_promise(promise, info) {
        const token = info.token = {};
        function update(type, index, key, value) {
            if (info.token !== token)
                return;
            info.resolved = value;
            let child_ctx = info.ctx;
            if (key !== undefined) {
                child_ctx = child_ctx.slice();
                child_ctx[key] = value;
            }
            const block = type && (info.current = type)(child_ctx);
            let needs_flush = false;
            if (info.block) {
                if (info.blocks) {
                    info.blocks.forEach((block, i) => {
                        if (i !== index && block) {
                            group_outros();
                            transition_out(block, 1, 1, () => {
                                if (info.blocks[i] === block) {
                                    info.blocks[i] = null;
                                }
                            });
                            check_outros();
                        }
                    });
                }
                else {
                    info.block.d(1);
                }
                block.c();
                transition_in(block, 1);
                block.m(info.mount(), info.anchor);
                needs_flush = true;
            }
            info.block = block;
            if (info.blocks)
                info.blocks[index] = block;
            if (needs_flush) {
                flush();
            }
        }
        if (is_promise(promise)) {
            const current_component = get_current_component();
            promise.then(value => {
                set_current_component(current_component);
                update(info.then, 1, info.value, value);
                set_current_component(null);
            }, error => {
                set_current_component(current_component);
                update(info.catch, 2, info.error, error);
                set_current_component(null);
                if (!info.hasCatch) {
                    throw error;
                }
            });
            // if we previously had a then/catch block, destroy it
            if (info.current !== info.pending) {
                update(info.pending, 0);
                return true;
            }
        }
        else {
            if (info.current !== info.then) {
                update(info.then, 1, info.value, promise);
                return true;
            }
            info.resolved = promise;
        }
    }
    function update_await_block_branch(info, ctx, dirty) {
        const child_ctx = ctx.slice();
        const { resolved } = info;
        if (info.current === info.then) {
            child_ctx[info.value] = resolved;
        }
        if (info.current === info.catch) {
            child_ctx[info.error] = resolved;
        }
        info.block.p(child_ctx, dirty);
    }
    function outro_and_destroy_block(block, lookup) {
        transition_out(block, 1, 1, () => {
            lookup.delete(block.key);
        });
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

    function create_fragment$3(ctx) {
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

    let devUrl$1 = "https://local.doctoctoc.net";
    let createSocialUserPath = "/moderation/api/create-twitter-socialuser/";

    function instance$2($$self, $$props, $$invalidate) {
    	let { screenName } = $$props;

    	function getApiUrl() {
    		if (window.location.hostname == "localhost") {
    			return devUrl$1 + createSocialUserPath + screenName + "/";
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
    		init(this, options, instance$2, create_fragment$3, safe_not_equal, { screenName: 0 });
    	}
    }

    /* src/HealthCareProvider.svelte generated by Svelte v3.38.3 */

    function get_each_context$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[3] = list[i];
    	return child_ctx;
    }

    function get_each_context_1$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[8] = list[i];
    	return child_ctx;
    }

    // (1:0) <script>     import { onMount }
    function create_catch_block(ctx) {
    	return { c: noop, m: noop, p: noop, d: noop };
    }

    // (43:29)  <ul> {#if data.length == 0}
    function create_then_block(ctx) {
    	let ul;
    	let t;
    	let if_block = /*data*/ ctx[1].length == 0 && create_if_block$1(ctx);
    	let each_value = /*data*/ ctx[1];
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$1(get_each_context$1(ctx, each_value, i));
    	}

    	return {
    		c() {
    			ul = element("ul");
    			if (if_block) if_block.c();
    			t = space();

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}
    		},
    		m(target, anchor) {
    			insert(target, ul, anchor);
    			if (if_block) if_block.m(ul, null);
    			append(ul, t);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(ul, null);
    			}
    		},
    		p(ctx, dirty) {
    			if (/*data*/ ctx[1].length == 0) if_block.p(ctx, dirty);

    			if (dirty & /*fetchApi, getBaseUrl*/ 4) {
    				each_value = /*data*/ ctx[1];
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$1(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$1(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(ul, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}
    		},
    		d(detaching) {
    			if (detaching) detach(ul);
    			if (if_block) if_block.d();
    			destroy_each(each_blocks, detaching);
    		}
    	};
    }

    // (45:0) {#if data.length == 0}
    function create_if_block$1(ctx) {
    	let li;
    	let a;
    	let t;
    	let a_href_value;

    	return {
    		c() {
    			li = element("li");
    			a = element("a");
    			t = text("🔗 HealthCareProvider admin");
    			attr(a, "href", a_href_value = "" + (getBaseUrl$1() + "/admin/hcp/healthcareprovider/add/?human=" + /*humanId*/ ctx[0]));
    			attr(a, "target", "_blank");
    		},
    		m(target, anchor) {
    			insert(target, li, anchor);
    			append(li, a);
    			append(a, t);
    		},
    		p(ctx, dirty) {
    			if (dirty & /*humanId*/ 1 && a_href_value !== (a_href_value = "" + (getBaseUrl$1() + "/admin/hcp/healthcareprovider/add/?human=" + /*humanId*/ ctx[0]))) {
    				attr(a, "href", a_href_value);
    			}
    		},
    		d(detaching) {
    			if (detaching) detach(li);
    		}
    	};
    }

    // (54:2) {#each hcp.taxonomy as taxonomy}
    function create_each_block_1$1(ctx) {
    	let li;
    	let t0_value = /*taxonomy*/ ctx[8].grouping + "";
    	let t0;
    	let t1;
    	let t2_value = /*taxonomy*/ ctx[8].classification + "";
    	let t2;
    	let t3;
    	let t4_value = /*taxonomy*/ ctx[8].specialization + "";
    	let t4;
    	let t5;

    	return {
    		c() {
    			li = element("li");
    			t0 = text(t0_value);
    			t1 = text(" | ");
    			t2 = text(t2_value);
    			t3 = space();
    			t4 = text(t4_value);
    			t5 = space();
    		},
    		m(target, anchor) {
    			insert(target, li, anchor);
    			append(li, t0);
    			append(li, t1);
    			append(li, t2);
    			append(li, t3);
    			append(li, t4);
    			append(li, t5);
    		},
    		p: noop,
    		d(detaching) {
    			if (detaching) detach(li);
    		}
    	};
    }

    // (50:0) {#each data as hcp}
    function create_each_block$1(ctx) {
    	let li;
    	let a;
    	let t0;
    	let a_href_value;
    	let t1;
    	let each_1_anchor;
    	let each_value_1 = /*hcp*/ ctx[3].taxonomy;
    	let each_blocks = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks[i] = create_each_block_1$1(get_each_context_1$1(ctx, each_value_1, i));
    	}

    	return {
    		c() {
    			li = element("li");
    			a = element("a");
    			t0 = text("🔗 HealthCareProvider admin");
    			t1 = space();

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			each_1_anchor = empty();
    			attr(a, "href", a_href_value = "" + (getBaseUrl$1() + "/admin/hcp/healthcareprovider/" + /*hcp*/ ctx[3].id + "/change/"));
    			attr(a, "target", "_blank");
    		},
    		m(target, anchor) {
    			insert(target, li, anchor);
    			append(li, a);
    			append(a, t0);
    			insert(target, t1, anchor);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(target, anchor);
    			}

    			insert(target, each_1_anchor, anchor);
    		},
    		p(ctx, dirty) {
    			if (dirty & /*fetchApi*/ 4) {
    				each_value_1 = /*hcp*/ ctx[3].taxonomy;
    				let i;

    				for (i = 0; i < each_value_1.length; i += 1) {
    					const child_ctx = get_each_context_1$1(ctx, each_value_1, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_1$1(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(each_1_anchor.parentNode, each_1_anchor);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value_1.length;
    			}
    		},
    		d(detaching) {
    			if (detaching) detach(li);
    			if (detaching) detach(t1);
    			destroy_each(each_blocks, detaching);
    			if (detaching) detach(each_1_anchor);
    		}
    	};
    }

    // (1:0) <script>     import { onMount }
    function create_pending_block(ctx) {
    	return { c: noop, m: noop, p: noop, d: noop };
    }

    function create_fragment$2(ctx) {
    	let await_block_anchor;

    	let info = {
    		ctx,
    		current: null,
    		token: null,
    		hasCatch: false,
    		pending: create_pending_block,
    		then: create_then_block,
    		catch: create_catch_block,
    		value: 1
    	};

    	handle_promise(/*fetchApi*/ ctx[2](), info);

    	return {
    		c() {
    			await_block_anchor = empty();
    			info.block.c();
    		},
    		m(target, anchor) {
    			insert(target, await_block_anchor, anchor);
    			info.block.m(target, info.anchor = anchor);
    			info.mount = () => await_block_anchor.parentNode;
    			info.anchor = await_block_anchor;
    		},
    		p(new_ctx, [dirty]) {
    			ctx = new_ctx;
    			update_await_block_branch(info, ctx, dirty);
    		},
    		i: noop,
    		o: noop,
    		d(detaching) {
    			if (detaching) detach(await_block_anchor);
    			info.block.d(detaching);
    			info.token = null;
    			info = null;
    		}
    	};
    }

    let devUrl = "https://local.doctoctoc.net";
    let apiPath$1 = "/hcp/api/hcp/";
    let apiProtocolDomain$1 = "https://local.doctoctoc.net";

    function getBaseUrl$1() {
    	if (window.location.hostname == "localhost") {
    		return apiProtocolDomain$1;
    	} else {
    		return "";
    	}
    }

    function instance$1($$self, $$props, $$invalidate) {
    	let { humanId } = $$props;
    	let hcp;
    	let data;

    	onMount(async () => {
    		$$invalidate(1, data = await fetchApi());
    		console.log(humanId);
    	});

    	function getApiUrl() {
    		let queryString = "?human__id=" + humanId;

    		if (window.location.hostname == "localhost") {
    			return devUrl + apiPath$1 + queryString;
    		} else {
    			return apiPath$1 + queryString;
    		}
    	}

    	async function fetchApi() {
    		let url = getApiUrl();
    		console.log(url);
    		let response = await await fetch(url);
    		let data = await response.json();
    		console.log(data);
    		return data;
    	}

    	

    	$$self.$$set = $$props => {
    		if ("humanId" in $$props) $$invalidate(0, humanId = $$props.humanId);
    	};

    	return [humanId, data, fetchApi, hcp];
    }

    class HealthCareProvider extends SvelteComponent {
    	constructor(options) {
    		super();
    		init(this, options, instance$1, create_fragment$2, safe_not_equal, { humanId: 0 });
    	}
    }

    /* src/UserName.svelte generated by Svelte v3.38.3 */

    function get_each_context(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[9] = list[i];
    	child_ctx[10] = list;
    	child_ctx[11] = i;
    	return child_ctx;
    }

    function get_each_context_1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[12] = list[i];
    	return child_ctx;
    }

    // (55:24) 
    function create_if_block_1(ctx) {
    	let each_blocks = [];
    	let each_1_lookup = new Map();
    	let each_1_anchor;
    	let current;
    	let each_value = /*socialusers*/ ctx[2];
    	const get_key = ctx => /*socialuser*/ ctx[9].id;

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
    			current = true;
    		},
    		p(ctx, dirty) {
    			if (dirty & /*socialusers, getBaseUrl*/ 4) {
    				each_value = /*socialusers*/ ctx[2];
    				group_outros();
    				each_blocks = update_keyed_each(each_blocks, dirty, get_key, 1, ctx, each_value, each_1_lookup, each_1_anchor.parentNode, outro_and_destroy_block, create_each_block, each_1_anchor, get_each_context);
    				check_outros();
    			}
    		},
    		i(local) {
    			if (current) return;

    			for (let i = 0; i < each_value.length; i += 1) {
    				transition_in(each_blocks[i]);
    			}

    			current = true;
    		},
    		o(local) {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				transition_out(each_blocks[i]);
    			}

    			current = false;
    		},
    		d(detaching) {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].d(detaching);
    			}

    			if (detaching) detach(each_1_anchor);
    		}
    	};
    }

    // (52:2) {#if socialusers && socialusers.length == 0 && screenName}
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

    // (65:22) {#each socialuser.category as cat}
    function create_each_block_1(ctx) {
    	let li;
    	let t_value = /*cat*/ ctx[12].label + "";
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
    			if (dirty & /*socialusers*/ 4 && t_value !== (t_value = /*cat*/ ctx[12].label + "")) set_data(t, t_value);
    		},
    		d(detaching) {
    			if (detaching) detach(li);
    		}
    	};
    }

    // (56:4) {#each socialusers as socialuser (socialuser.id) }
    function create_each_block(key_1, ctx) {
    	let div;
    	let ul1;
    	let li0;
    	let img;
    	let img_src_value;
    	let t0;
    	let li1;
    	let t1;
    	let t2_value = /*socialuser*/ ctx[9].id + "";
    	let t2;
    	let t3;
    	let li2;
    	let a0;
    	let t4;
    	let a0_href_value;
    	let t5;
    	let li3;
    	let t6;
    	let t7_value = /*socialuser*/ ctx[9].user_id + "";
    	let t7;
    	let t8;
    	let li4;
    	let t9;
    	let t10_value = /*socialuser*/ ctx[9].profile.json.screen_name + "";
    	let t10;
    	let t11;
    	let li5;
    	let t12;
    	let t13_value = /*socialuser*/ ctx[9].profile.json.name + "";
    	let t13;
    	let t14;
    	let li6;
    	let t15;
    	let ul0;
    	let t16;
    	let li7;
    	let a1;
    	let t17;
    	let a1_href_value;
    	let t18;
    	let li8;
    	let t19;
    	let healthcareprovider;
    	let updating_humanId;
    	let t20;
    	let current;
    	let each_value_1 = /*socialuser*/ ctx[9].category;
    	let each_blocks = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks[i] = create_each_block_1(get_each_context_1(ctx, each_value_1, i));
    	}

    	function healthcareprovider_humanId_binding(value) {
    		/*healthcareprovider_humanId_binding*/ ctx[6](value, /*socialuser*/ ctx[9]);
    	}

    	let healthcareprovider_props = {};

    	if (/*socialuser*/ ctx[9].human[0].id !== void 0) {
    		healthcareprovider_props.humanId = /*socialuser*/ ctx[9].human[0].id;
    	}

    	healthcareprovider = new HealthCareProvider({ props: healthcareprovider_props });
    	binding_callbacks.push(() => bind(healthcareprovider, "humanId", healthcareprovider_humanId_binding));

    	return {
    		key: key_1,
    		first: null,
    		c() {
    			div = element("div");
    			ul1 = element("ul");
    			li0 = element("li");
    			img = element("img");
    			t0 = space();
    			li1 = element("li");
    			t1 = text("SocialUser id: ");
    			t2 = text(t2_value);
    			t3 = space();
    			li2 = element("li");
    			a0 = element("a");
    			t4 = text("🔗 Twitter profile");
    			t5 = space();
    			li3 = element("li");
    			t6 = text("Twitter user id: ");
    			t7 = text(t7_value);
    			t8 = space();
    			li4 = element("li");
    			t9 = text("Twitter screen name: ");
    			t10 = text(t10_value);
    			t11 = space();
    			li5 = element("li");
    			t12 = text("Twitter name: ");
    			t13 = text(t13_value);
    			t14 = space();
    			li6 = element("li");
    			t15 = text("category");
    			ul0 = element("ul");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			t16 = space();
    			li7 = element("li");
    			a1 = element("a");
    			t17 = text("🔗 SocialUser admin");
    			t18 = space();
    			li8 = element("li");
    			t19 = text("Health Care Provider ");
    			create_component(healthcareprovider.$$.fragment);
    			t20 = space();
    			if (img.src !== (img_src_value = /*socialuser*/ ctx[9].profile.biggeravatar)) attr(img, "src", img_src_value);
    			attr(img, "alt", "user avatar");
    			attr(a0, "href", a0_href_value = "https://twitter.com/intent/user?user_id=" + /*socialuser*/ ctx[9].profile.json.id_str);
    			attr(a0, "target", "_blank");
    			attr(ul0, "class", "svelte-7jz005");
    			attr(a1, "href", a1_href_value = "" + (getBaseUrl() + "/admin/moderation/socialuser/" + /*socialuser*/ ctx[9].id + "/change/"));
    			attr(a1, "target", "_blank");
    			attr(ul1, "class", "svelte-7jz005");
    			attr(div, "class", "parent");
    			this.first = div;
    		},
    		m(target, anchor) {
    			insert(target, div, anchor);
    			append(div, ul1);
    			append(ul1, li0);
    			append(li0, img);
    			append(ul1, t0);
    			append(ul1, li1);
    			append(li1, t1);
    			append(li1, t2);
    			append(ul1, t3);
    			append(ul1, li2);
    			append(li2, a0);
    			append(a0, t4);
    			append(ul1, t5);
    			append(ul1, li3);
    			append(li3, t6);
    			append(li3, t7);
    			append(ul1, t8);
    			append(ul1, li4);
    			append(li4, t9);
    			append(li4, t10);
    			append(ul1, t11);
    			append(ul1, li5);
    			append(li5, t12);
    			append(li5, t13);
    			append(ul1, t14);
    			append(ul1, li6);
    			append(li6, t15);
    			append(li6, ul0);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(ul0, null);
    			}

    			append(ul1, t16);
    			append(ul1, li7);
    			append(li7, a1);
    			append(a1, t17);
    			append(li7, t18);
    			append(ul1, li8);
    			append(li8, t19);
    			mount_component(healthcareprovider, li8, null);
    			append(div, t20);
    			current = true;
    		},
    		p(new_ctx, dirty) {
    			ctx = new_ctx;

    			if (!current || dirty & /*socialusers*/ 4 && img.src !== (img_src_value = /*socialuser*/ ctx[9].profile.biggeravatar)) {
    				attr(img, "src", img_src_value);
    			}

    			if ((!current || dirty & /*socialusers*/ 4) && t2_value !== (t2_value = /*socialuser*/ ctx[9].id + "")) set_data(t2, t2_value);

    			if (!current || dirty & /*socialusers*/ 4 && a0_href_value !== (a0_href_value = "https://twitter.com/intent/user?user_id=" + /*socialuser*/ ctx[9].profile.json.id_str)) {
    				attr(a0, "href", a0_href_value);
    			}

    			if ((!current || dirty & /*socialusers*/ 4) && t7_value !== (t7_value = /*socialuser*/ ctx[9].user_id + "")) set_data(t7, t7_value);
    			if ((!current || dirty & /*socialusers*/ 4) && t10_value !== (t10_value = /*socialuser*/ ctx[9].profile.json.screen_name + "")) set_data(t10, t10_value);
    			if ((!current || dirty & /*socialusers*/ 4) && t13_value !== (t13_value = /*socialuser*/ ctx[9].profile.json.name + "")) set_data(t13, t13_value);

    			if (dirty & /*socialusers*/ 4) {
    				each_value_1 = /*socialuser*/ ctx[9].category;
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

    			if (!current || dirty & /*socialusers*/ 4 && a1_href_value !== (a1_href_value = "" + (getBaseUrl() + "/admin/moderation/socialuser/" + /*socialuser*/ ctx[9].id + "/change/"))) {
    				attr(a1, "href", a1_href_value);
    			}

    			const healthcareprovider_changes = {};

    			if (!updating_humanId && dirty & /*socialusers*/ 4) {
    				updating_humanId = true;
    				healthcareprovider_changes.humanId = /*socialuser*/ ctx[9].human[0].id;
    				add_flush_callback(() => updating_humanId = false);
    			}

    			healthcareprovider.$set(healthcareprovider_changes);
    		},
    		i(local) {
    			if (current) return;
    			transition_in(healthcareprovider.$$.fragment, local);
    			current = true;
    		},
    		o(local) {
    			transition_out(healthcareprovider.$$.fragment, local);
    			current = false;
    		},
    		d(detaching) {
    			if (detaching) detach(div);
    			destroy_each(each_blocks, detaching);
    			destroy_component(healthcareprovider);
    		}
    	};
    }

    // (51:2) {#key socialusers}
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
    			console.log(data);
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

    	function healthcareprovider_humanId_binding(value, socialuser) {
    		if ($$self.$$.not_equal(socialuser.human[0].id, value)) {
    			socialuser.human[0].id = value;
    			$$invalidate(2, socialusers);
    		}
    	}

    	return [
    		input,
    		screenName,
    		socialusers,
    		onClickFetchApi,
    		input_1_input_handler,
    		createsocialuser_screenName_binding,
    		healthcareprovider_humanId_binding
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
    			attr(main, "class", "svelte-d02qci");
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
