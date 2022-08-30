
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
    let src_url_equal_anchor;
    function src_url_equal(element_src, url) {
        if (!src_url_equal_anchor) {
            src_url_equal_anchor = document.createElement('a');
        }
        src_url_equal_anchor.href = url;
        return element_src === src_url_equal_anchor.href;
    }
    function is_empty(obj) {
        return Object.keys(obj).length === 0;
    }
    function append(target, node) {
        target.appendChild(node);
    }
    function insert(target, node, anchor) {
        target.insertBefore(node, anchor || null);
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
    function set_style(node, key, value, important) {
        if (value === null) {
            node.style.removeProperty(key);
        }
        else {
            node.style.setProperty(key, value, important ? 'important' : '');
        }
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
    // flush() calls callbacks in this order:
    // 1. All beforeUpdate callbacks, in order: parents before children
    // 2. All bind:this callbacks, in reverse order: children before parents.
    // 3. All afterUpdate callbacks, in order: parents before children. EXCEPT
    //    for afterUpdates called during the initial onMount, which are called in
    //    reverse order: children before parents.
    // Since callbacks might update component values, which could trigger another
    // call to flush(), the following steps guard against this:
    // 1. During beforeUpdate, any updated components will be added to the
    //    dirty_components array and will cause a reentrant call to flush(). Because
    //    the flush index is kept outside the function, the reentrant call will pick
    //    up where the earlier call left off and go through all dirty components. The
    //    current_component value is saved and restored so that the reentrant call will
    //    not interfere with the "parent" flush() call.
    // 2. bind:this callbacks cannot trigger new flush() calls.
    // 3. During afterUpdate, any updated components will NOT have their afterUpdate
    //    callback called a second time; the seen_callbacks set, outside the flush()
    //    function, guarantees this behavior.
    const seen_callbacks = new Set();
    let flushidx = 0; // Do *not* move this inside the flush() function
    function flush() {
        const saved_component = current_component;
        do {
            // first, call beforeUpdate functions
            // and update components
            while (flushidx < dirty_components.length) {
                const component = dirty_components[flushidx];
                flushidx++;
                set_current_component(component);
                update(component.$$);
            }
            set_current_component(null);
            dirty_components.length = 0;
            flushidx = 0;
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
        seen_callbacks.clear();
        set_current_component(saved_component);
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
    function init(component, options, instance, create_fragment, not_equal, props, append_styles, dirty = [-1]) {
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
            context: new Map(options.context || (parent_component ? parent_component.$$.context : [])),
            // everything else
            callbacks: blank_object(),
            dirty,
            skip_bound: false,
            root: options.target || parent_component.$$.root
        };
        append_styles && append_styles($$.root);
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

    /* src/CreateSocialUser.svelte generated by Svelte v3.46.4 */

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
    		if ('screenName' in $$props) $$invalidate(0, screenName = $$props.screenName);
    	};

    	return [screenName, fetchApi];
    }

    class CreateSocialUser extends SvelteComponent {
    	constructor(options) {
    		super();
    		init(this, options, instance$2, create_fragment$3, safe_not_equal, { screenName: 0 });
    	}
    }

    /* src/HealthCareProvider.svelte generated by Svelte v3.46.4 */

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
    			attr(a, "href", a_href_value = "" + (getBaseUrl() + "/admin/hcp/healthcareprovider/add/?human=" + /*humanId*/ ctx[0]));
    			attr(a, "target", "_blank");
    		},
    		m(target, anchor) {
    			insert(target, li, anchor);
    			append(li, a);
    			append(a, t);
    		},
    		p(ctx, dirty) {
    			if (dirty & /*humanId*/ 1 && a_href_value !== (a_href_value = "" + (getBaseUrl() + "/admin/hcp/healthcareprovider/add/?human=" + /*humanId*/ ctx[0]))) {
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
    			attr(a, "href", a_href_value = "" + (getBaseUrl() + "/admin/hcp/healthcareprovider/" + /*hcp*/ ctx[3].id + "/change/"));
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
    let apiProtocolDomain = "https://local.doctoctoc.net";

    function getBaseUrl() {
    	if (window.location.hostname == "localhost") {
    		return apiProtocolDomain;
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
    		if ('humanId' in $$props) $$invalidate(0, humanId = $$props.humanId);
    	};

    	return [humanId, data, fetchApi, hcp];
    }

    class HealthCareProvider extends SvelteComponent {
    	constructor(options) {
    		super();
    		init(this, options, instance$1, create_fragment$2, safe_not_equal, { humanId: 0 });
    	}
    }

    var commonjsGlobal = typeof globalThis !== 'undefined' ? globalThis : typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {};

    function createCommonjsModule(fn) {
      var module = { exports: {} };
    	return fn(module, module.exports), module.exports;
    }

    var dayjs_min = createCommonjsModule(function (module, exports) {
    !function(t,e){module.exports=e();}(commonjsGlobal,(function(){var t=1e3,e=6e4,n=36e5,r="millisecond",i="second",s="minute",u="hour",a="day",o="week",f="month",h="quarter",c="year",d="date",$="Invalid Date",l=/^(\d{4})[-/]?(\d{1,2})?[-/]?(\d{0,2})[Tt\s]*(\d{1,2})?:?(\d{1,2})?:?(\d{1,2})?[.:]?(\d+)?$/,y=/\[([^\]]+)]|Y{1,4}|M{1,4}|D{1,2}|d{1,4}|H{1,2}|h{1,2}|a|A|m{1,2}|s{1,2}|Z{1,2}|SSS/g,M={name:"en",weekdays:"Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday".split("_"),months:"January_February_March_April_May_June_July_August_September_October_November_December".split("_")},m=function(t,e,n){var r=String(t);return !r||r.length>=e?t:""+Array(e+1-r.length).join(n)+t},g={s:m,z:function(t){var e=-t.utcOffset(),n=Math.abs(e),r=Math.floor(n/60),i=n%60;return (e<=0?"+":"-")+m(r,2,"0")+":"+m(i,2,"0")},m:function t(e,n){if(e.date()<n.date())return -t(n,e);var r=12*(n.year()-e.year())+(n.month()-e.month()),i=e.clone().add(r,f),s=n-i<0,u=e.clone().add(r+(s?-1:1),f);return +(-(r+(n-i)/(s?i-u:u-i))||0)},a:function(t){return t<0?Math.ceil(t)||0:Math.floor(t)},p:function(t){return {M:f,y:c,w:o,d:a,D:d,h:u,m:s,s:i,ms:r,Q:h}[t]||String(t||"").toLowerCase().replace(/s$/,"")},u:function(t){return void 0===t}},v="en",D={};D[v]=M;var p=function(t){return t instanceof _},S=function t(e,n,r){var i;if(!e)return v;if("string"==typeof e){var s=e.toLowerCase();D[s]&&(i=s),n&&(D[s]=n,i=s);var u=e.split("-");if(!i&&u.length>1)return t(u[0])}else {var a=e.name;D[a]=e,i=a;}return !r&&i&&(v=i),i||!r&&v},w=function(t,e){if(p(t))return t.clone();var n="object"==typeof e?e:{};return n.date=t,n.args=arguments,new _(n)},O=g;O.l=S,O.i=p,O.w=function(t,e){return w(t,{locale:e.$L,utc:e.$u,x:e.$x,$offset:e.$offset})};var _=function(){function M(t){this.$L=S(t.locale,null,!0),this.parse(t);}var m=M.prototype;return m.parse=function(t){this.$d=function(t){var e=t.date,n=t.utc;if(null===e)return new Date(NaN);if(O.u(e))return new Date;if(e instanceof Date)return new Date(e);if("string"==typeof e&&!/Z$/i.test(e)){var r=e.match(l);if(r){var i=r[2]-1||0,s=(r[7]||"0").substring(0,3);return n?new Date(Date.UTC(r[1],i,r[3]||1,r[4]||0,r[5]||0,r[6]||0,s)):new Date(r[1],i,r[3]||1,r[4]||0,r[5]||0,r[6]||0,s)}}return new Date(e)}(t),this.$x=t.x||{},this.init();},m.init=function(){var t=this.$d;this.$y=t.getFullYear(),this.$M=t.getMonth(),this.$D=t.getDate(),this.$W=t.getDay(),this.$H=t.getHours(),this.$m=t.getMinutes(),this.$s=t.getSeconds(),this.$ms=t.getMilliseconds();},m.$utils=function(){return O},m.isValid=function(){return !(this.$d.toString()===$)},m.isSame=function(t,e){var n=w(t);return this.startOf(e)<=n&&n<=this.endOf(e)},m.isAfter=function(t,e){return w(t)<this.startOf(e)},m.isBefore=function(t,e){return this.endOf(e)<w(t)},m.$g=function(t,e,n){return O.u(t)?this[e]:this.set(n,t)},m.unix=function(){return Math.floor(this.valueOf()/1e3)},m.valueOf=function(){return this.$d.getTime()},m.startOf=function(t,e){var n=this,r=!!O.u(e)||e,h=O.p(t),$=function(t,e){var i=O.w(n.$u?Date.UTC(n.$y,e,t):new Date(n.$y,e,t),n);return r?i:i.endOf(a)},l=function(t,e){return O.w(n.toDate()[t].apply(n.toDate("s"),(r?[0,0,0,0]:[23,59,59,999]).slice(e)),n)},y=this.$W,M=this.$M,m=this.$D,g="set"+(this.$u?"UTC":"");switch(h){case c:return r?$(1,0):$(31,11);case f:return r?$(1,M):$(0,M+1);case o:var v=this.$locale().weekStart||0,D=(y<v?y+7:y)-v;return $(r?m-D:m+(6-D),M);case a:case d:return l(g+"Hours",0);case u:return l(g+"Minutes",1);case s:return l(g+"Seconds",2);case i:return l(g+"Milliseconds",3);default:return this.clone()}},m.endOf=function(t){return this.startOf(t,!1)},m.$set=function(t,e){var n,o=O.p(t),h="set"+(this.$u?"UTC":""),$=(n={},n[a]=h+"Date",n[d]=h+"Date",n[f]=h+"Month",n[c]=h+"FullYear",n[u]=h+"Hours",n[s]=h+"Minutes",n[i]=h+"Seconds",n[r]=h+"Milliseconds",n)[o],l=o===a?this.$D+(e-this.$W):e;if(o===f||o===c){var y=this.clone().set(d,1);y.$d[$](l),y.init(),this.$d=y.set(d,Math.min(this.$D,y.daysInMonth())).$d;}else $&&this.$d[$](l);return this.init(),this},m.set=function(t,e){return this.clone().$set(t,e)},m.get=function(t){return this[O.p(t)]()},m.add=function(r,h){var d,$=this;r=Number(r);var l=O.p(h),y=function(t){var e=w($);return O.w(e.date(e.date()+Math.round(t*r)),$)};if(l===f)return this.set(f,this.$M+r);if(l===c)return this.set(c,this.$y+r);if(l===a)return y(1);if(l===o)return y(7);var M=(d={},d[s]=e,d[u]=n,d[i]=t,d)[l]||1,m=this.$d.getTime()+r*M;return O.w(m,this)},m.subtract=function(t,e){return this.add(-1*t,e)},m.format=function(t){var e=this,n=this.$locale();if(!this.isValid())return n.invalidDate||$;var r=t||"YYYY-MM-DDTHH:mm:ssZ",i=O.z(this),s=this.$H,u=this.$m,a=this.$M,o=n.weekdays,f=n.months,h=function(t,n,i,s){return t&&(t[n]||t(e,r))||i[n].slice(0,s)},c=function(t){return O.s(s%12||12,t,"0")},d=n.meridiem||function(t,e,n){var r=t<12?"AM":"PM";return n?r.toLowerCase():r},l={YY:String(this.$y).slice(-2),YYYY:this.$y,M:a+1,MM:O.s(a+1,2,"0"),MMM:h(n.monthsShort,a,f,3),MMMM:h(f,a),D:this.$D,DD:O.s(this.$D,2,"0"),d:String(this.$W),dd:h(n.weekdaysMin,this.$W,o,2),ddd:h(n.weekdaysShort,this.$W,o,3),dddd:o[this.$W],H:String(s),HH:O.s(s,2,"0"),h:c(1),hh:c(2),a:d(s,u,!0),A:d(s,u,!1),m:String(u),mm:O.s(u,2,"0"),s:String(this.$s),ss:O.s(this.$s,2,"0"),SSS:O.s(this.$ms,3,"0"),Z:i};return r.replace(y,(function(t,e){return e||l[t]||i.replace(":","")}))},m.utcOffset=function(){return 15*-Math.round(this.$d.getTimezoneOffset()/15)},m.diff=function(r,d,$){var l,y=O.p(d),M=w(r),m=(M.utcOffset()-this.utcOffset())*e,g=this-M,v=O.m(this,M);return v=(l={},l[c]=v/12,l[f]=v,l[h]=v/3,l[o]=(g-m)/6048e5,l[a]=(g-m)/864e5,l[u]=g/n,l[s]=g/e,l[i]=g/t,l)[y]||g,$?v:O.a(v)},m.daysInMonth=function(){return this.endOf(f).$D},m.$locale=function(){return D[this.$L]},m.locale=function(t,e){if(!t)return this.$L;var n=this.clone(),r=S(t,e,!0);return r&&(n.$L=r),n},m.clone=function(){return O.w(this.$d,this)},m.toDate=function(){return new Date(this.valueOf())},m.toJSON=function(){return this.isValid()?this.toISOString():null},m.toISOString=function(){return this.$d.toISOString()},m.toString=function(){return this.$d.toUTCString()},M}(),T=_.prototype;return w.prototype=T,[["$ms",r],["$s",i],["$m",s],["$H",u],["$W",a],["$M",f],["$y",c],["$D",d]].forEach((function(t){T[t[1]]=function(e){return this.$g(e,t[0],t[1])};})),w.extend=function(t,e){return t.$i||(t(e,_,w),t.$i=!0),w},w.locale=S,w.isDayjs=p,w.unix=function(t){return w(1e3*t)},w.en=D[v],w.Ls=D,w.p={},w}));
    });

    var customParseFormat = createCommonjsModule(function (module, exports) {
    !function(e,t){module.exports=t();}(commonjsGlobal,(function(){var e={LTS:"h:mm:ss A",LT:"h:mm A",L:"MM/DD/YYYY",LL:"MMMM D, YYYY",LLL:"MMMM D, YYYY h:mm A",LLLL:"dddd, MMMM D, YYYY h:mm A"},t=/(\[[^[]*\])|([-_:/.,()\s]+)|(A|a|YYYY|YY?|MM?M?M?|Do|DD?|hh?|HH?|mm?|ss?|S{1,3}|z|ZZ?)/g,n=/\d\d/,r=/\d\d?/,i=/\d*[^-_:/,()\s\d]+/,o={},s=function(e){return (e=+e)+(e>68?1900:2e3)};var a=function(e){return function(t){this[e]=+t;}},f=[/[+-]\d\d:?(\d\d)?|Z/,function(e){(this.zone||(this.zone={})).offset=function(e){if(!e)return 0;if("Z"===e)return 0;var t=e.match(/([+-]|\d\d)/g),n=60*t[1]+(+t[2]||0);return 0===n?0:"+"===t[0]?-n:n}(e);}],h=function(e){var t=o[e];return t&&(t.indexOf?t:t.s.concat(t.f))},u=function(e,t){var n,r=o.meridiem;if(r){for(var i=1;i<=24;i+=1)if(e.indexOf(r(i,0,t))>-1){n=i>12;break}}else n=e===(t?"pm":"PM");return n},d={A:[i,function(e){this.afternoon=u(e,!1);}],a:[i,function(e){this.afternoon=u(e,!0);}],S:[/\d/,function(e){this.milliseconds=100*+e;}],SS:[n,function(e){this.milliseconds=10*+e;}],SSS:[/\d{3}/,function(e){this.milliseconds=+e;}],s:[r,a("seconds")],ss:[r,a("seconds")],m:[r,a("minutes")],mm:[r,a("minutes")],H:[r,a("hours")],h:[r,a("hours")],HH:[r,a("hours")],hh:[r,a("hours")],D:[r,a("day")],DD:[n,a("day")],Do:[i,function(e){var t=o.ordinal,n=e.match(/\d+/);if(this.day=n[0],t)for(var r=1;r<=31;r+=1)t(r).replace(/\[|\]/g,"")===e&&(this.day=r);}],M:[r,a("month")],MM:[n,a("month")],MMM:[i,function(e){var t=h("months"),n=(h("monthsShort")||t.map((function(e){return e.slice(0,3)}))).indexOf(e)+1;if(n<1)throw new Error;this.month=n%12||n;}],MMMM:[i,function(e){var t=h("months").indexOf(e)+1;if(t<1)throw new Error;this.month=t%12||t;}],Y:[/[+-]?\d+/,a("year")],YY:[n,function(e){this.year=s(e);}],YYYY:[/\d{4}/,a("year")],Z:f,ZZ:f};function c(n){var r,i;r=n,i=o&&o.formats;for(var s=(n=r.replace(/(\[[^\]]+])|(LTS?|l{1,4}|L{1,4})/g,(function(t,n,r){var o=r&&r.toUpperCase();return n||i[r]||e[r]||i[o].replace(/(\[[^\]]+])|(MMMM|MM|DD|dddd)/g,(function(e,t,n){return t||n.slice(1)}))}))).match(t),a=s.length,f=0;f<a;f+=1){var h=s[f],u=d[h],c=u&&u[0],l=u&&u[1];s[f]=l?{regex:c,parser:l}:h.replace(/^\[|\]$/g,"");}return function(e){for(var t={},n=0,r=0;n<a;n+=1){var i=s[n];if("string"==typeof i)r+=i.length;else {var o=i.regex,f=i.parser,h=e.slice(r),u=o.exec(h)[0];f.call(t,u),e=e.replace(u,"");}}return function(e){var t=e.afternoon;if(void 0!==t){var n=e.hours;t?n<12&&(e.hours+=12):12===n&&(e.hours=0),delete e.afternoon;}}(t),t}}return function(e,t,n){n.p.customParseFormat=!0,e&&e.parseTwoDigitYear&&(s=e.parseTwoDigitYear);var r=t.prototype,i=r.parse;r.parse=function(e){var t=e.date,r=e.utc,s=e.args;this.$u=r;var a=s[1];if("string"==typeof a){var f=!0===s[2],h=!0===s[3],u=f||h,d=s[2];h&&(d=s[2]),o=this.$locale(),!f&&d&&(o=n.Ls[d]),this.$d=function(e,t,n){try{if(["x","X"].indexOf(t)>-1)return new Date(("X"===t?1e3:1)*e);var r=c(t)(e),i=r.year,o=r.month,s=r.day,a=r.hours,f=r.minutes,h=r.seconds,u=r.milliseconds,d=r.zone,l=new Date,m=s||(i||o?1:l.getDate()),M=i||l.getFullYear(),Y=0;i&&!o||(Y=o>0?o-1:l.getMonth());var p=a||0,v=f||0,D=h||0,g=u||0;return d?new Date(Date.UTC(M,Y,m,p,v,D,g+60*d.offset*1e3)):n?new Date(Date.UTC(M,Y,m,p,v,D,g)):new Date(M,Y,m,p,v,D,g)}catch(e){return new Date("")}}(t,a,r),this.init(),d&&!0!==d&&(this.$L=this.locale(d).$L),u&&t!=this.format(a)&&(this.$d=new Date("")),o={};}else if(a instanceof Array)for(var l=a.length,m=1;m<=l;m+=1){s[1]=a[m-1];var M=n.apply(this,s);if(M.isValid()){this.$d=M.$d,this.$L=M.$L,this.init();break}m===l&&(this.$d=new Date(""));}else i.call(this,e);};}}));
    });

    var relativeTime = createCommonjsModule(function (module, exports) {
    !function(r,e){module.exports=e();}(commonjsGlobal,(function(){return function(r,e,t){r=r||{};var n=e.prototype,o={future:"in %s",past:"%s ago",s:"a few seconds",m:"a minute",mm:"%d minutes",h:"an hour",hh:"%d hours",d:"a day",dd:"%d days",M:"a month",MM:"%d months",y:"a year",yy:"%d years"};function i(r,e,t,o){return n.fromToBase(r,e,t,o)}t.en.relativeTime=o,n.fromToBase=function(e,n,i,d,u){for(var f,a,s,l=i.$locale().relativeTime||o,h=r.thresholds||[{l:"s",r:44,d:"second"},{l:"m",r:89},{l:"mm",r:44,d:"minute"},{l:"h",r:89},{l:"hh",r:21,d:"hour"},{l:"d",r:35},{l:"dd",r:25,d:"day"},{l:"M",r:45},{l:"MM",r:10,d:"month"},{l:"y",r:17},{l:"yy",d:"year"}],m=h.length,c=0;c<m;c+=1){var y=h[c];y.d&&(f=d?t(e).diff(i,y.d,!0):i.diff(e,y.d,!0));var p=(r.rounding||Math.round)(Math.abs(f));if(s=f>0,p<=y.r||!y.r){p<=1&&c>0&&(y=h[c-1]);var v=l[y.l];u&&(p=u(""+p)),a="string"==typeof v?v.replace("%d",p):v(p,n,y.l,s);break}}if(n)return a;var M=s?l.future:l.past;return "function"==typeof M?M(a):M.replace("%s",a)},n.to=function(r,e){return i(r,e,this,!0)},n.from=function(r,e){return i(r,e,this)};var d=function(r){return r.$u?t.utc():t()};n.toNow=function(r){return this.to(d(this),r)},n.fromNow=function(r){return this.from(d(this),r)};}}));
    });

    createCommonjsModule(function (module, exports) {
    !function(e,n){module.exports=n(dayjs_min);}(commonjsGlobal,(function(e){function n(e){return e&&"object"==typeof e&&"default"in e?e:{default:e}}var t=n(e),i={name:"fr",weekdays:"dimanche_lundi_mardi_mercredi_jeudi_vendredi_samedi".split("_"),weekdaysShort:"dim._lun._mar._mer._jeu._ven._sam.".split("_"),weekdaysMin:"di_lu_ma_me_je_ve_sa".split("_"),months:"janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre".split("_"),monthsShort:"janv._févr._mars_avr._mai_juin_juil._août_sept._oct._nov._déc.".split("_"),weekStart:1,yearStart:4,formats:{LT:"HH:mm",LTS:"HH:mm:ss",L:"DD/MM/YYYY",LL:"D MMMM YYYY",LLL:"D MMMM YYYY HH:mm",LLLL:"dddd D MMMM YYYY HH:mm"},relativeTime:{future:"dans %s",past:"il y a %s",s:"quelques secondes",m:"une minute",mm:"%d minutes",h:"une heure",hh:"%d heures",d:"un jour",dd:"%d jours",M:"un mois",MM:"%d mois",y:"un an",yy:"%d ans"},ordinal:function(e){return ""+e+(1===e?"er":"e")}};return t.default.locale(i,null,!0),i}));
    });

    /* src/UserName.svelte generated by Svelte v3.46.4 */

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

    // (83:23) 
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
    			if (dirty & /*socialusers, toHRDate, durationFromNow*/ 12) {
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

    // (80:1) {#if socialusers && socialusers.length == 0 && screenName}
    function create_if_block(ctx) {
    	let p;
    	let t1;
    	let createsocialuser;
    	let updating_screenName;
    	let current;

    	function createsocialuser_screenName_binding(value) {
    		/*createsocialuser_screenName_binding*/ ctx[6](value);
    	}

    	let createsocialuser_props = {};

    	if (/*screenName*/ ctx[1] !== void 0) {
    		createsocialuser_props.screenName = /*screenName*/ ctx[1];
    	}

    	createsocialuser = new CreateSocialUser({ props: createsocialuser_props });
    	binding_callbacks.push(() => bind(createsocialuser, 'screenName', createsocialuser_screenName_binding));

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

    // (119:10) {#if catRel.moderator}
    function create_if_block_2(ctx) {
    	let t0;
    	let t1_value = /*catRel*/ ctx[12].moderator.profile.json.screen_name + "";
    	let t1;
    	let if_block = /*catRel*/ ctx[12].moderator.id == /*socialuser*/ ctx[9].id && create_if_block_3();

    	return {
    		c() {
    			if (if_block) if_block.c();
    			t0 = text(" | ");
    			t1 = text(t1_value);
    		},
    		m(target, anchor) {
    			if (if_block) if_block.m(target, anchor);
    			insert(target, t0, anchor);
    			insert(target, t1, anchor);
    		},
    		p(ctx, dirty) {
    			if (/*catRel*/ ctx[12].moderator.id == /*socialuser*/ ctx[9].id) {
    				if (if_block) ; else {
    					if_block = create_if_block_3();
    					if_block.c();
    					if_block.m(t0.parentNode, t0);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}

    			if (dirty & /*socialusers*/ 4 && t1_value !== (t1_value = /*catRel*/ ctx[12].moderator.profile.json.screen_name + "")) set_data(t1, t1_value);
    		},
    		d(detaching) {
    			if (if_block) if_block.d(detaching);
    			if (detaching) detach(t0);
    			if (detaching) detach(t1);
    		}
    	};
    }

    // (120:11) {#if catRel.moderator.id == socialuser.id}
    function create_if_block_3(ctx) {
    	let mark;

    	return {
    		c() {
    			mark = element("mark");
    			mark.textContent = "*";
    		},
    		m(target, anchor) {
    			insert(target, mark, anchor);
    		},
    		d(detaching) {
    			if (detaching) detach(mark);
    		}
    	};
    }

    // (115:7) {#each socialuser.categoryrelationships as catRel}
    function create_each_block_1(ctx) {
    	let li;
    	let div;
    	let t0_value = /*catRel*/ ctx[12].category.label + "";
    	let t0;
    	let t1;
    	let t2;
    	let t3_value = toHRDate(/*catRel*/ ctx[12].created) + "";
    	let t3;
    	let t4;
    	let t5_value = toHRDate(/*catRel*/ ctx[12].updated) + "";
    	let t5;
    	let t6;
    	let if_block = /*catRel*/ ctx[12].moderator && create_if_block_2(ctx);

    	return {
    		c() {
    			li = element("li");
    			div = element("div");
    			t0 = text(t0_value);
    			t1 = space();
    			if (if_block) if_block.c();
    			t2 = text("\n\t\t\t\t\t\t\t\t\t\t| Created ");
    			t3 = text(t3_value);
    			t4 = text(" | Updated\n\t\t\t\t\t\t\t\t\t\t");
    			t5 = text(t5_value);
    			t6 = space();
    			set_style(div, "white-space", "nowrap");
    		},
    		m(target, anchor) {
    			insert(target, li, anchor);
    			append(li, div);
    			append(div, t0);
    			append(div, t1);
    			if (if_block) if_block.m(div, null);
    			append(div, t2);
    			append(div, t3);
    			append(div, t4);
    			append(div, t5);
    			append(li, t6);
    		},
    		p(ctx, dirty) {
    			if (dirty & /*socialusers*/ 4 && t0_value !== (t0_value = /*catRel*/ ctx[12].category.label + "")) set_data(t0, t0_value);

    			if (/*catRel*/ ctx[12].moderator) {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block_2(ctx);
    					if_block.c();
    					if_block.m(div, t2);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}

    			if (dirty & /*socialusers*/ 4 && t3_value !== (t3_value = toHRDate(/*catRel*/ ctx[12].created) + "")) set_data(t3, t3_value);
    			if (dirty & /*socialusers*/ 4 && t5_value !== (t5_value = toHRDate(/*catRel*/ ctx[12].updated) + "")) set_data(t5, t5_value);
    		},
    		d(detaching) {
    			if (detaching) detach(li);
    			if (if_block) if_block.d();
    		}
    	};
    }

    // (84:2) {#each socialusers as socialuser (socialuser.id)}
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
    	let t16_value = /*durationFromNow*/ ctx[3](/*socialuser*/ ctx[9].profile.json.created_at) + "";
    	let t16;
    	let t17;
    	let li7;
    	let t18_value = /*socialuser*/ ctx[9].profile.json.description + "";
    	let t18;
    	let t19;
    	let li8;
    	let t20;
    	let t21_value = /*socialuser*/ ctx[9].profile.json.location + "";
    	let t21;
    	let t22;
    	let li9;
    	let t23;
    	let t24_value = /*socialuser*/ ctx[9].profile.json.statuses_count + "";
    	let t24;
    	let t25;
    	let li10;
    	let t26;
    	let t27_value = /*socialuser*/ ctx[9].profile.json.favourites_count + "";
    	let t27;
    	let t28;
    	let li11;
    	let t29;
    	let ul0;
    	let t30;
    	let li12;
    	let a1;
    	let t31;
    	let a1_href_value;
    	let t32;
    	let li13;
    	let t33;
    	let healthcareprovider;
    	let updating_humanId;
    	let t34;
    	let current;
    	let each_value_1 = /*socialuser*/ ctx[9].categoryrelationships;
    	let each_blocks = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks[i] = create_each_block_1(get_each_context_1(ctx, each_value_1, i));
    	}

    	function healthcareprovider_humanId_binding(value) {
    		/*healthcareprovider_humanId_binding*/ ctx[7](value, /*socialuser*/ ctx[9]);
    	}

    	let healthcareprovider_props = {};

    	if (/*socialuser*/ ctx[9].human[0].id !== void 0) {
    		healthcareprovider_props.humanId = /*socialuser*/ ctx[9].human[0].id;
    	}

    	healthcareprovider = new HealthCareProvider({ props: healthcareprovider_props });
    	binding_callbacks.push(() => bind(healthcareprovider, 'humanId', healthcareprovider_humanId_binding));

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
    			t15 = text("Account created ");
    			t16 = text(t16_value);
    			t17 = space();
    			li7 = element("li");
    			t18 = text(t18_value);
    			t19 = space();
    			li8 = element("li");
    			t20 = text("location: ");
    			t21 = text(t21_value);
    			t22 = space();
    			li9 = element("li");
    			t23 = text("statuses count: ");
    			t24 = text(t24_value);
    			t25 = space();
    			li10 = element("li");
    			t26 = text("favourites count: ");
    			t27 = text(t27_value);
    			t28 = space();
    			li11 = element("li");
    			t29 = text("category\n\t\t\t\t\t\t");
    			ul0 = element("ul");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			t30 = space();
    			li12 = element("li");
    			a1 = element("a");
    			t31 = text("🔗 SocialUser admin");
    			t32 = space();
    			li13 = element("li");
    			t33 = text("Health Care Provider ");
    			create_component(healthcareprovider.$$.fragment);
    			t34 = space();
    			if (!src_url_equal(img.src, img_src_value = /*socialuser*/ ctx[9].profile.biggeravatar)) attr(img, "src", img_src_value);
    			attr(img, "alt", "user avatar");
    			attr(a0, "href", a0_href_value = "https://twitter.com/intent/user?user_id=" + /*socialuser*/ ctx[9].profile.json.id_str);
    			attr(a0, "target", "_blank");
    			attr(ul0, "class", "svelte-sm5shj");
    			attr(a1, "href", a1_href_value = "/admin/moderation/socialuser/" + /*socialuser*/ ctx[9].id + "/change/");
    			attr(a1, "target", "_blank");
    			attr(ul1, "class", "svelte-sm5shj");
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
    			append(li6, t16);
    			append(ul1, t17);
    			append(ul1, li7);
    			append(li7, t18);
    			append(ul1, t19);
    			append(ul1, li8);
    			append(li8, t20);
    			append(li8, t21);
    			append(ul1, t22);
    			append(ul1, li9);
    			append(li9, t23);
    			append(li9, t24);
    			append(ul1, t25);
    			append(ul1, li10);
    			append(li10, t26);
    			append(li10, t27);
    			append(ul1, t28);
    			append(ul1, li11);
    			append(li11, t29);
    			append(li11, ul0);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(ul0, null);
    			}

    			append(ul1, t30);
    			append(ul1, li12);
    			append(li12, a1);
    			append(a1, t31);
    			append(ul1, t32);
    			append(ul1, li13);
    			append(li13, t33);
    			mount_component(healthcareprovider, li13, null);
    			append(div, t34);
    			current = true;
    		},
    		p(new_ctx, dirty) {
    			ctx = new_ctx;

    			if (!current || dirty & /*socialusers*/ 4 && !src_url_equal(img.src, img_src_value = /*socialuser*/ ctx[9].profile.biggeravatar)) {
    				attr(img, "src", img_src_value);
    			}

    			if ((!current || dirty & /*socialusers*/ 4) && t2_value !== (t2_value = /*socialuser*/ ctx[9].id + "")) set_data(t2, t2_value);

    			if (!current || dirty & /*socialusers*/ 4 && a0_href_value !== (a0_href_value = "https://twitter.com/intent/user?user_id=" + /*socialuser*/ ctx[9].profile.json.id_str)) {
    				attr(a0, "href", a0_href_value);
    			}

    			if ((!current || dirty & /*socialusers*/ 4) && t7_value !== (t7_value = /*socialuser*/ ctx[9].user_id + "")) set_data(t7, t7_value);
    			if ((!current || dirty & /*socialusers*/ 4) && t10_value !== (t10_value = /*socialuser*/ ctx[9].profile.json.screen_name + "")) set_data(t10, t10_value);
    			if ((!current || dirty & /*socialusers*/ 4) && t13_value !== (t13_value = /*socialuser*/ ctx[9].profile.json.name + "")) set_data(t13, t13_value);
    			if ((!current || dirty & /*socialusers*/ 4) && t16_value !== (t16_value = /*durationFromNow*/ ctx[3](/*socialuser*/ ctx[9].profile.json.created_at) + "")) set_data(t16, t16_value);
    			if ((!current || dirty & /*socialusers*/ 4) && t18_value !== (t18_value = /*socialuser*/ ctx[9].profile.json.description + "")) set_data(t18, t18_value);
    			if ((!current || dirty & /*socialusers*/ 4) && t21_value !== (t21_value = /*socialuser*/ ctx[9].profile.json.location + "")) set_data(t21, t21_value);
    			if ((!current || dirty & /*socialusers*/ 4) && t24_value !== (t24_value = /*socialuser*/ ctx[9].profile.json.statuses_count + "")) set_data(t24, t24_value);
    			if ((!current || dirty & /*socialusers*/ 4) && t27_value !== (t27_value = /*socialuser*/ ctx[9].profile.json.favourites_count + "")) set_data(t27, t27_value);

    			if (dirty & /*toHRDate, socialusers*/ 4) {
    				each_value_1 = /*socialuser*/ ctx[9].categoryrelationships;
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

    			if (!current || dirty & /*socialusers*/ 4 && a1_href_value !== (a1_href_value = "/admin/moderation/socialuser/" + /*socialuser*/ ctx[9].id + "/change/")) {
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

    // (79:0) {#key socialusers}
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
    					listen(input_1, "input", /*input_1_input_handler*/ ctx[5]),
    					listen(button, "click", function () {
    						if (is_function(/*onClickFetchApi*/ ctx[4](/*input*/ ctx[0]))) /*onClickFetchApi*/ ctx[4](/*input*/ ctx[0]).apply(this, arguments);
    					}),
    					listen(form, "submit", prevent_default(function () {
    						if (is_function(/*onClickFetchApi*/ ctx[4](/*input*/ ctx[0]))) /*onClickFetchApi*/ ctx[4](/*input*/ ctx[0]).apply(this, arguments);
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

    let apiPath = "/moderation/api/socialuser/";

    function toHRDate(isoDateTimeString) {
    	const date = new Date(isoDateTimeString);
    	return date.toDateString();
    }

    function instance($$self, $$props, $$invalidate) {
    	dayjs_min.extend(customParseFormat);
    	dayjs_min.extend(relativeTime);
    	let input = "";
    	let screenName = "";
    	let socialusers = null;

    	function durationFromNow(twitterDateTimeString) {
    		//Twitter date time format: "Thu Jun 05 19:56:42 +0000 2014"
    		let dateTime = dayjs_min(twitterDateTimeString, "[ddd] MMM DD HH:mm:ss [zz] YYYY");

    		return dateTime.fromNow();
    	}

    	async function fetchApi(sn) {
    		let url = apiPath + "?search=" + sn;

    		await fetch(url).then(r => r.json()).then(data => {
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

    		$$invalidate(2, socialusers = await fetchApi(screenName));
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

    	{
    		let param = new URL(document.location).searchParams.get("screen_name");

    		if (param) {
    			$$invalidate(2, socialusers = fetchApi(param));
    			$$invalidate(1, screenName = param);
    			$$invalidate(0, input = param);
    		}
    	}

    	return [
    		input,
    		screenName,
    		socialusers,
    		durationFromNow,
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

    /* src/App.svelte generated by Svelte v3.46.4 */

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

})();
//# sourceMappingURL=bundle.js.map
