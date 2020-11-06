
(function(l, r) { if (l.getElementById('livereloadscript')) return; r = l.createElement('script'); r.async = 1; r.src = '//' + (window.location.host || 'localhost').split(':')[0] + ':35729/livereload.js?snipver=1'; r.id = 'livereloadscript'; l.getElementsByTagName('head')[0].appendChild(r) })(window.document);
var app = (function () {
    'use strict';

    function noop() { }
    function assign(tar, src) {
        // @ts-ignore
        for (const k in src)
            tar[k] = src[k];
        return tar;
    }
    function add_location(element, file, line, column, char) {
        element.__svelte_meta = {
            loc: { file, line, column, char }
        };
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
    function validate_store(store, name) {
        if (store != null && typeof store.subscribe !== 'function') {
            throw new Error(`'${name}' is not a store with a 'subscribe' method`);
        }
    }
    function subscribe(store, ...callbacks) {
        if (store == null) {
            return noop;
        }
        const unsub = store.subscribe(...callbacks);
        return unsub.unsubscribe ? () => unsub.unsubscribe() : unsub;
    }
    function component_subscribe(component, store, callback) {
        component.$$.on_destroy.push(subscribe(store, callback));
    }
    function create_slot(definition, ctx, $$scope, fn) {
        if (definition) {
            const slot_ctx = get_slot_context(definition, ctx, $$scope, fn);
            return definition[0](slot_ctx);
        }
    }
    function get_slot_context(definition, ctx, $$scope, fn) {
        return definition[1] && fn
            ? assign($$scope.ctx.slice(), definition[1](fn(ctx)))
            : $$scope.ctx;
    }
    function get_slot_changes(definition, $$scope, dirty, fn) {
        if (definition[2] && fn) {
            const lets = definition[2](fn(dirty));
            if ($$scope.dirty === undefined) {
                return lets;
            }
            if (typeof lets === 'object') {
                const merged = [];
                const len = Math.max($$scope.dirty.length, lets.length);
                for (let i = 0; i < len; i += 1) {
                    merged[i] = $$scope.dirty[i] | lets[i];
                }
                return merged;
            }
            return $$scope.dirty | lets;
        }
        return $$scope.dirty;
    }
    function update_slot(slot, slot_definition, ctx, $$scope, dirty, get_slot_changes_fn, get_slot_context_fn) {
        const slot_changes = get_slot_changes(slot_definition, $$scope, dirty, get_slot_changes_fn);
        if (slot_changes) {
            const slot_context = get_slot_context(slot_definition, ctx, $$scope, get_slot_context_fn);
            slot.p(slot_context, slot_changes);
        }
    }
    function exclude_internal_props(props) {
        const result = {};
        for (const k in props)
            if (k[0] !== '$')
                result[k] = props[k];
        return result;
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
    function attr(node, attribute, value) {
        if (value == null)
            node.removeAttribute(attribute);
        else if (node.getAttribute(attribute) !== value)
            node.setAttribute(attribute, value);
    }
    function set_attributes(node, attributes) {
        // @ts-ignore
        const descriptors = Object.getOwnPropertyDescriptors(node.__proto__);
        for (const key in attributes) {
            if (attributes[key] == null) {
                node.removeAttribute(key);
            }
            else if (key === 'style') {
                node.style.cssText = attributes[key];
            }
            else if (key === '__value') {
                node.value = node[key] = attributes[key];
            }
            else if (descriptors[key] && descriptors[key].set) {
                node[key] = attributes[key];
            }
            else {
                attr(node, key, attributes[key]);
            }
        }
    }
    function get_binding_group_value(group, __value, checked) {
        const value = new Set();
        for (let i = 0; i < group.length; i += 1) {
            if (group[i].checked)
                value.add(group[i].__value);
        }
        if (!checked) {
            value.delete(__value);
        }
        return Array.from(value);
    }
    function children(element) {
        return Array.from(element.childNodes);
    }
    function set_style(node, key, value, important) {
        node.style.setProperty(key, value, important ? 'important' : '');
    }
    function custom_event(type, detail) {
        const e = document.createEvent('CustomEvent');
        e.initCustomEvent(type, false, false, detail);
        return e;
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
    function onDestroy(fn) {
        get_current_component().$$.on_destroy.push(fn);
    }
    function createEventDispatcher() {
        const component = get_current_component();
        return (type, detail) => {
            const callbacks = component.$$.callbacks[type];
            if (callbacks) {
                // TODO are there situations where events could be dispatched
                // in a server (non-DOM) environment?
                const event = custom_event(type, detail);
                callbacks.slice().forEach(fn => {
                    fn.call(component, event);
                });
            }
        };
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

    const globals = (typeof window !== 'undefined'
        ? window
        : typeof globalThis !== 'undefined'
            ? globalThis
            : global);

    function get_spread_update(levels, updates) {
        const update = {};
        const to_null_out = {};
        const accounted_for = { $$scope: 1 };
        let i = levels.length;
        while (i--) {
            const o = levels[i];
            const n = updates[i];
            if (n) {
                for (const key in o) {
                    if (!(key in n))
                        to_null_out[key] = 1;
                }
                for (const key in n) {
                    if (!accounted_for[key]) {
                        update[key] = n[key];
                        accounted_for[key] = 1;
                    }
                }
                levels[i] = n;
            }
            else {
                for (const key in o) {
                    accounted_for[key] = 1;
                }
            }
        }
        for (const key in to_null_out) {
            if (!(key in update))
                update[key] = undefined;
        }
        return update;
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
    function mount_component(component, target, anchor) {
        const { fragment, on_mount, on_destroy, after_update } = component.$$;
        fragment && fragment.m(target, anchor);
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
        const prop_values = options.props || {};
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
            before_update: [],
            after_update: [],
            context: new Map(parent_component ? parent_component.$$.context : []),
            // everything else
            callbacks: blank_object(),
            dirty,
            skip_bound: false
        };
        let ready = false;
        $$.ctx = instance
            ? instance(component, prop_values, (i, ret, ...rest) => {
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
            mount_component(component, options.target, options.anchor);
            flush();
        }
        set_current_component(parent_component);
    }
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

    function dispatch_dev(type, detail) {
        document.dispatchEvent(custom_event(type, Object.assign({ version: '3.29.4' }, detail)));
    }
    function append_dev(target, node) {
        dispatch_dev('SvelteDOMInsert', { target, node });
        append(target, node);
    }
    function insert_dev(target, node, anchor) {
        dispatch_dev('SvelteDOMInsert', { target, node, anchor });
        insert(target, node, anchor);
    }
    function detach_dev(node) {
        dispatch_dev('SvelteDOMRemove', { node });
        detach(node);
    }
    function listen_dev(node, event, handler, options, has_prevent_default, has_stop_propagation) {
        const modifiers = options === true ? ['capture'] : options ? Array.from(Object.keys(options)) : [];
        if (has_prevent_default)
            modifiers.push('preventDefault');
        if (has_stop_propagation)
            modifiers.push('stopPropagation');
        dispatch_dev('SvelteDOMAddEventListener', { node, event, handler, modifiers });
        const dispose = listen(node, event, handler, options);
        return () => {
            dispatch_dev('SvelteDOMRemoveEventListener', { node, event, handler, modifiers });
            dispose();
        };
    }
    function attr_dev(node, attribute, value) {
        attr(node, attribute, value);
        if (value == null)
            dispatch_dev('SvelteDOMRemoveAttribute', { node, attribute });
        else
            dispatch_dev('SvelteDOMSetAttribute', { node, attribute, value });
    }
    function prop_dev(node, property, value) {
        node[property] = value;
        dispatch_dev('SvelteDOMSetProperty', { node, property, value });
    }
    function set_data_dev(text, data) {
        data = '' + data;
        if (text.wholeText === data)
            return;
        dispatch_dev('SvelteDOMSetData', { node: text, data });
        text.data = data;
    }
    function validate_each_argument(arg) {
        if (typeof arg !== 'string' && !(arg && typeof arg === 'object' && 'length' in arg)) {
            let msg = '{#each} only iterates over array-like objects.';
            if (typeof Symbol === 'function' && arg && Symbol.iterator in arg) {
                msg += ' You can use a spread to convert this iterable into an array.';
            }
            throw new Error(msg);
        }
    }
    function validate_slots(name, slot, keys) {
        for (const slot_key of Object.keys(slot)) {
            if (!~keys.indexOf(slot_key)) {
                console.warn(`<${name}> received an unexpected slot "${slot_key}".`);
            }
        }
    }
    class SvelteComponentDev extends SvelteComponent {
        constructor(options) {
            if (!options || (!options.target && !options.$$inline)) {
                throw new Error("'target' is a required option");
            }
            super();
        }
        $destroy() {
            super.$destroy();
            this.$destroy = () => {
                console.warn('Component was already destroyed'); // eslint-disable-line no-console
            };
        }
        $capture_state() { }
        $inject_state() { }
    }

    const subscriber_queue = [];
    /**
     * Creates a `Readable` store that allows reading by subscription.
     * @param value initial value
     * @param {StartStopNotifier}start start and stop notifications for subscriptions
     */
    function readable(value, start) {
        return {
            subscribe: writable(value, start).subscribe
        };
    }
    /**
     * Create a `Writable` store that allows both updating and reading by subscription.
     * @param {*=}value initial value
     * @param {StartStopNotifier=}start start and stop notifications for subscriptions
     */
    function writable(value, start = noop) {
        let stop;
        const subscribers = [];
        function set(new_value) {
            if (safe_not_equal(value, new_value)) {
                value = new_value;
                if (stop) { // store is ready
                    const run_queue = !subscriber_queue.length;
                    for (let i = 0; i < subscribers.length; i += 1) {
                        const s = subscribers[i];
                        s[1]();
                        subscriber_queue.push(s, value);
                    }
                    if (run_queue) {
                        for (let i = 0; i < subscriber_queue.length; i += 2) {
                            subscriber_queue[i][0](subscriber_queue[i + 1]);
                        }
                        subscriber_queue.length = 0;
                    }
                }
            }
        }
        function update(fn) {
            set(fn(value));
        }
        function subscribe(run, invalidate = noop) {
            const subscriber = [run, invalidate];
            subscribers.push(subscriber);
            if (subscribers.length === 1) {
                stop = start(set) || noop;
            }
            run(value);
            return () => {
                const index = subscribers.indexOf(subscriber);
                if (index !== -1) {
                    subscribers.splice(index, 1);
                }
                if (subscribers.length === 0) {
                    stop();
                    stop = null;
                }
            };
        }
        return { set, update, subscribe };
    }
    function derived(stores, fn, initial_value) {
        const single = !Array.isArray(stores);
        const stores_array = single
            ? [stores]
            : stores;
        const auto = fn.length < 2;
        return readable(initial_value, (set) => {
            let inited = false;
            const values = [];
            let pending = 0;
            let cleanup = noop;
            const sync = () => {
                if (pending) {
                    return;
                }
                cleanup();
                const result = fn(single ? values[0] : values, set);
                if (auto) {
                    set(result);
                }
                else {
                    cleanup = is_function(result) ? result : noop;
                }
            };
            const unsubscribers = stores_array.map((store, i) => subscribe(store, (value) => {
                values[i] = value;
                pending &= ~(1 << i);
                if (inited) {
                    sync();
                }
            }, () => {
                pending |= (1 << i);
            }));
            inited = true;
            sync();
            return function stop() {
                run_all(unsubscribers);
                cleanup();
            };
        });
    }

    var TYPE;
    (function (TYPE) {
        /**
         * Raw text
         */
        TYPE[TYPE["literal"] = 0] = "literal";
        /**
         * Variable w/o any format, e.g `var` in `this is a {var}`
         */
        TYPE[TYPE["argument"] = 1] = "argument";
        /**
         * Variable w/ number format
         */
        TYPE[TYPE["number"] = 2] = "number";
        /**
         * Variable w/ date format
         */
        TYPE[TYPE["date"] = 3] = "date";
        /**
         * Variable w/ time format
         */
        TYPE[TYPE["time"] = 4] = "time";
        /**
         * Variable w/ select format
         */
        TYPE[TYPE["select"] = 5] = "select";
        /**
         * Variable w/ plural format
         */
        TYPE[TYPE["plural"] = 6] = "plural";
        /**
         * Only possible within plural argument.
         * This is the `#` symbol that will be substituted with the count.
         */
        TYPE[TYPE["pound"] = 7] = "pound";
    })(TYPE || (TYPE = {}));
    /**
     * Type Guards
     */
    function isLiteralElement(el) {
        return el.type === TYPE.literal;
    }
    function isArgumentElement(el) {
        return el.type === TYPE.argument;
    }
    function isNumberElement(el) {
        return el.type === TYPE.number;
    }
    function isDateElement(el) {
        return el.type === TYPE.date;
    }
    function isTimeElement(el) {
        return el.type === TYPE.time;
    }
    function isSelectElement(el) {
        return el.type === TYPE.select;
    }
    function isPluralElement(el) {
        return el.type === TYPE.plural;
    }
    function isPoundElement(el) {
        return el.type === TYPE.pound;
    }
    function isNumberSkeleton(el) {
        return !!(el && typeof el === 'object' && el.type === 0 /* number */);
    }
    function isDateTimeSkeleton(el) {
        return !!(el && typeof el === 'object' && el.type === 1 /* dateTime */);
    }

    // tslint:disable:only-arrow-functions
    // tslint:disable:object-literal-shorthand
    // tslint:disable:trailing-comma
    // tslint:disable:object-literal-sort-keys
    // tslint:disable:one-variable-per-declaration
    // tslint:disable:max-line-length
    // tslint:disable:no-consecutive-blank-lines
    // tslint:disable:align
    var __extends = (undefined && undefined.__extends) || (function () {
        var extendStatics = function (d, b) {
            extendStatics = Object.setPrototypeOf ||
                ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
                function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
            return extendStatics(d, b);
        };
        return function (d, b) {
            extendStatics(d, b);
            function __() { this.constructor = d; }
            d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
        };
    })();
    var __assign = (undefined && undefined.__assign) || function () {
        __assign = Object.assign || function(t) {
            for (var s, i = 1, n = arguments.length; i < n; i++) {
                s = arguments[i];
                for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                    t[p] = s[p];
            }
            return t;
        };
        return __assign.apply(this, arguments);
    };
    var SyntaxError = /** @class */ (function (_super) {
        __extends(SyntaxError, _super);
        function SyntaxError(message, expected, found, location) {
            var _this = _super.call(this) || this;
            _this.message = message;
            _this.expected = expected;
            _this.found = found;
            _this.location = location;
            _this.name = "SyntaxError";
            if (typeof Error.captureStackTrace === "function") {
                Error.captureStackTrace(_this, SyntaxError);
            }
            return _this;
        }
        SyntaxError.buildMessage = function (expected, found) {
            function hex(ch) {
                return ch.charCodeAt(0).toString(16).toUpperCase();
            }
            function literalEscape(s) {
                return s
                    .replace(/\\/g, "\\\\")
                    .replace(/"/g, "\\\"")
                    .replace(/\0/g, "\\0")
                    .replace(/\t/g, "\\t")
                    .replace(/\n/g, "\\n")
                    .replace(/\r/g, "\\r")
                    .replace(/[\x00-\x0F]/g, function (ch) { return "\\x0" + hex(ch); })
                    .replace(/[\x10-\x1F\x7F-\x9F]/g, function (ch) { return "\\x" + hex(ch); });
            }
            function classEscape(s) {
                return s
                    .replace(/\\/g, "\\\\")
                    .replace(/\]/g, "\\]")
                    .replace(/\^/g, "\\^")
                    .replace(/-/g, "\\-")
                    .replace(/\0/g, "\\0")
                    .replace(/\t/g, "\\t")
                    .replace(/\n/g, "\\n")
                    .replace(/\r/g, "\\r")
                    .replace(/[\x00-\x0F]/g, function (ch) { return "\\x0" + hex(ch); })
                    .replace(/[\x10-\x1F\x7F-\x9F]/g, function (ch) { return "\\x" + hex(ch); });
            }
            function describeExpectation(expectation) {
                switch (expectation.type) {
                    case "literal":
                        return "\"" + literalEscape(expectation.text) + "\"";
                    case "class":
                        var escapedParts = expectation.parts.map(function (part) {
                            return Array.isArray(part)
                                ? classEscape(part[0]) + "-" + classEscape(part[1])
                                : classEscape(part);
                        });
                        return "[" + (expectation.inverted ? "^" : "") + escapedParts + "]";
                    case "any":
                        return "any character";
                    case "end":
                        return "end of input";
                    case "other":
                        return expectation.description;
                }
            }
            function describeExpected(expected1) {
                var descriptions = expected1.map(describeExpectation);
                var i;
                var j;
                descriptions.sort();
                if (descriptions.length > 0) {
                    for (i = 1, j = 1; i < descriptions.length; i++) {
                        if (descriptions[i - 1] !== descriptions[i]) {
                            descriptions[j] = descriptions[i];
                            j++;
                        }
                    }
                    descriptions.length = j;
                }
                switch (descriptions.length) {
                    case 1:
                        return descriptions[0];
                    case 2:
                        return descriptions[0] + " or " + descriptions[1];
                    default:
                        return descriptions.slice(0, -1).join(", ")
                            + ", or "
                            + descriptions[descriptions.length - 1];
                }
            }
            function describeFound(found1) {
                return found1 ? "\"" + literalEscape(found1) + "\"" : "end of input";
            }
            return "Expected " + describeExpected(expected) + " but " + describeFound(found) + " found.";
        };
        return SyntaxError;
    }(Error));
    function peg$parse(input, options) {
        options = options !== undefined ? options : {};
        var peg$FAILED = {};
        var peg$startRuleFunctions = { start: peg$parsestart };
        var peg$startRuleFunction = peg$parsestart;
        var peg$c0 = function (parts) {
            return parts.join('');
        };
        var peg$c1 = function (messageText) {
            return __assign({ type: TYPE.literal, value: messageText }, insertLocation());
        };
        var peg$c2 = "#";
        var peg$c3 = peg$literalExpectation("#", false);
        var peg$c4 = function () {
            return __assign({ type: TYPE.pound }, insertLocation());
        };
        var peg$c5 = peg$otherExpectation("argumentElement");
        var peg$c6 = "{";
        var peg$c7 = peg$literalExpectation("{", false);
        var peg$c8 = "}";
        var peg$c9 = peg$literalExpectation("}", false);
        var peg$c10 = function (value) {
            return __assign({ type: TYPE.argument, value: value }, insertLocation());
        };
        var peg$c11 = peg$otherExpectation("numberSkeletonId");
        var peg$c12 = /^['\/{}]/;
        var peg$c13 = peg$classExpectation(["'", "/", "{", "}"], false, false);
        var peg$c14 = peg$anyExpectation();
        var peg$c15 = peg$otherExpectation("numberSkeletonTokenOption");
        var peg$c16 = "/";
        var peg$c17 = peg$literalExpectation("/", false);
        var peg$c18 = function (option) { return option; };
        var peg$c19 = peg$otherExpectation("numberSkeletonToken");
        var peg$c20 = function (stem, options) {
            return { stem: stem, options: options };
        };
        var peg$c21 = function (tokens) {
            return __assign({ type: 0 /* number */, tokens: tokens }, insertLocation());
        };
        var peg$c22 = "::";
        var peg$c23 = peg$literalExpectation("::", false);
        var peg$c24 = function (skeleton) { return skeleton; };
        var peg$c25 = function () { messageCtx.push('numberArgStyle'); return true; };
        var peg$c26 = function (style) {
            messageCtx.pop();
            return style.replace(/\s*$/, '');
        };
        var peg$c27 = ",";
        var peg$c28 = peg$literalExpectation(",", false);
        var peg$c29 = "number";
        var peg$c30 = peg$literalExpectation("number", false);
        var peg$c31 = function (value, type, style) {
            return __assign({ type: type === 'number' ? TYPE.number : type === 'date' ? TYPE.date : TYPE.time, style: style && style[2], value: value }, insertLocation());
        };
        var peg$c32 = "'";
        var peg$c33 = peg$literalExpectation("'", false);
        var peg$c34 = /^[^']/;
        var peg$c35 = peg$classExpectation(["'"], true, false);
        var peg$c36 = /^[^a-zA-Z'{}]/;
        var peg$c37 = peg$classExpectation([["a", "z"], ["A", "Z"], "'", "{", "}"], true, false);
        var peg$c38 = /^[a-zA-Z]/;
        var peg$c39 = peg$classExpectation([["a", "z"], ["A", "Z"]], false, false);
        var peg$c40 = function (pattern) {
            return __assign({ type: 1 /* dateTime */, pattern: pattern }, insertLocation());
        };
        var peg$c41 = function () { messageCtx.push('dateOrTimeArgStyle'); return true; };
        var peg$c42 = "date";
        var peg$c43 = peg$literalExpectation("date", false);
        var peg$c44 = "time";
        var peg$c45 = peg$literalExpectation("time", false);
        var peg$c46 = "plural";
        var peg$c47 = peg$literalExpectation("plural", false);
        var peg$c48 = "selectordinal";
        var peg$c49 = peg$literalExpectation("selectordinal", false);
        var peg$c50 = "offset:";
        var peg$c51 = peg$literalExpectation("offset:", false);
        var peg$c52 = function (value, pluralType, offset, options) {
            return __assign({ type: TYPE.plural, pluralType: pluralType === 'plural' ? 'cardinal' : 'ordinal', value: value, offset: offset ? offset[2] : 0, options: options.reduce(function (all, _a) {
                    var id = _a.id, value = _a.value, optionLocation = _a.location;
                    if (id in all) {
                        error("Duplicate option \"" + id + "\" in plural element: \"" + text() + "\"", location());
                    }
                    all[id] = {
                        value: value,
                        location: optionLocation
                    };
                    return all;
                }, {}) }, insertLocation());
        };
        var peg$c53 = "select";
        var peg$c54 = peg$literalExpectation("select", false);
        var peg$c55 = function (value, options) {
            return __assign({ type: TYPE.select, value: value, options: options.reduce(function (all, _a) {
                    var id = _a.id, value = _a.value, optionLocation = _a.location;
                    if (id in all) {
                        error("Duplicate option \"" + id + "\" in select element: \"" + text() + "\"", location());
                    }
                    all[id] = {
                        value: value,
                        location: optionLocation
                    };
                    return all;
                }, {}) }, insertLocation());
        };
        var peg$c56 = "=";
        var peg$c57 = peg$literalExpectation("=", false);
        var peg$c58 = function (id) { messageCtx.push('select'); return true; };
        var peg$c59 = function (id, value) {
            messageCtx.pop();
            return __assign({ id: id,
                value: value }, insertLocation());
        };
        var peg$c60 = function (id) { messageCtx.push('plural'); return true; };
        var peg$c61 = function (id, value) {
            messageCtx.pop();
            return __assign({ id: id,
                value: value }, insertLocation());
        };
        var peg$c62 = peg$otherExpectation("whitespace");
        var peg$c63 = /^[\t-\r \x85\xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000]/;
        var peg$c64 = peg$classExpectation([["\t", "\r"], " ", "\x85", "\xA0", "\u1680", ["\u2000", "\u200A"], "\u2028", "\u2029", "\u202F", "\u205F", "\u3000"], false, false);
        var peg$c65 = peg$otherExpectation("syntax pattern");
        var peg$c66 = /^[!-\/:-@[-\^`{-~\xA1-\xA7\xA9\xAB\xAC\xAE\xB0\xB1\xB6\xBB\xBF\xD7\xF7\u2010-\u2027\u2030-\u203E\u2041-\u2053\u2055-\u205E\u2190-\u245F\u2500-\u2775\u2794-\u2BFF\u2E00-\u2E7F\u3001-\u3003\u3008-\u3020\u3030\uFD3E\uFD3F\uFE45\uFE46]/;
        var peg$c67 = peg$classExpectation([["!", "/"], [":", "@"], ["[", "^"], "`", ["{", "~"], ["\xA1", "\xA7"], "\xA9", "\xAB", "\xAC", "\xAE", "\xB0", "\xB1", "\xB6", "\xBB", "\xBF", "\xD7", "\xF7", ["\u2010", "\u2027"], ["\u2030", "\u203E"], ["\u2041", "\u2053"], ["\u2055", "\u205E"], ["\u2190", "\u245F"], ["\u2500", "\u2775"], ["\u2794", "\u2BFF"], ["\u2E00", "\u2E7F"], ["\u3001", "\u3003"], ["\u3008", "\u3020"], "\u3030", "\uFD3E", "\uFD3F", "\uFE45", "\uFE46"], false, false);
        var peg$c68 = peg$otherExpectation("optional whitespace");
        var peg$c69 = peg$otherExpectation("number");
        var peg$c70 = "-";
        var peg$c71 = peg$literalExpectation("-", false);
        var peg$c72 = function (negative, num) {
            return num
                ? negative
                    ? -num
                    : num
                : 0;
        };
        var peg$c74 = peg$otherExpectation("double apostrophes");
        var peg$c75 = "''";
        var peg$c76 = peg$literalExpectation("''", false);
        var peg$c77 = function () { return "'"; };
        var peg$c78 = function (escapedChar, quotedChars) {
            return escapedChar + quotedChars.replace("''", "'");
        };
        var peg$c79 = function (x) {
            return (x !== '{' &&
                !(isInPluralOption() && x === '#') &&
                !(isNestedMessageText() && x === '}'));
        };
        var peg$c80 = "\n";
        var peg$c81 = peg$literalExpectation("\n", false);
        var peg$c82 = function (x) {
            return x === '{' || x === '}' || (isInPluralOption() && x === '#');
        };
        var peg$c83 = peg$otherExpectation("argNameOrNumber");
        var peg$c84 = peg$otherExpectation("argNumber");
        var peg$c85 = "0";
        var peg$c86 = peg$literalExpectation("0", false);
        var peg$c87 = function () { return 0; };
        var peg$c88 = /^[1-9]/;
        var peg$c89 = peg$classExpectation([["1", "9"]], false, false);
        var peg$c90 = /^[0-9]/;
        var peg$c91 = peg$classExpectation([["0", "9"]], false, false);
        var peg$c92 = function (digits) {
            return parseInt(digits.join(''), 10);
        };
        var peg$c93 = peg$otherExpectation("argName");
        var peg$currPos = 0;
        var peg$savedPos = 0;
        var peg$posDetailsCache = [{ line: 1, column: 1 }];
        var peg$maxFailPos = 0;
        var peg$maxFailExpected = [];
        var peg$silentFails = 0;
        var peg$result;
        if (options.startRule !== undefined) {
            if (!(options.startRule in peg$startRuleFunctions)) {
                throw new Error("Can't start parsing from rule \"" + options.startRule + "\".");
            }
            peg$startRuleFunction = peg$startRuleFunctions[options.startRule];
        }
        function text() {
            return input.substring(peg$savedPos, peg$currPos);
        }
        function location() {
            return peg$computeLocation(peg$savedPos, peg$currPos);
        }
        function error(message, location1) {
            location1 = location1 !== undefined
                ? location1
                : peg$computeLocation(peg$savedPos, peg$currPos);
            throw peg$buildSimpleError(message, location1);
        }
        function peg$literalExpectation(text1, ignoreCase) {
            return { type: "literal", text: text1, ignoreCase: ignoreCase };
        }
        function peg$classExpectation(parts, inverted, ignoreCase) {
            return { type: "class", parts: parts, inverted: inverted, ignoreCase: ignoreCase };
        }
        function peg$anyExpectation() {
            return { type: "any" };
        }
        function peg$endExpectation() {
            return { type: "end" };
        }
        function peg$otherExpectation(description) {
            return { type: "other", description: description };
        }
        function peg$computePosDetails(pos) {
            var details = peg$posDetailsCache[pos];
            var p;
            if (details) {
                return details;
            }
            else {
                p = pos - 1;
                while (!peg$posDetailsCache[p]) {
                    p--;
                }
                details = peg$posDetailsCache[p];
                details = {
                    line: details.line,
                    column: details.column
                };
                while (p < pos) {
                    if (input.charCodeAt(p) === 10) {
                        details.line++;
                        details.column = 1;
                    }
                    else {
                        details.column++;
                    }
                    p++;
                }
                peg$posDetailsCache[pos] = details;
                return details;
            }
        }
        function peg$computeLocation(startPos, endPos) {
            var startPosDetails = peg$computePosDetails(startPos);
            var endPosDetails = peg$computePosDetails(endPos);
            return {
                start: {
                    offset: startPos,
                    line: startPosDetails.line,
                    column: startPosDetails.column
                },
                end: {
                    offset: endPos,
                    line: endPosDetails.line,
                    column: endPosDetails.column
                }
            };
        }
        function peg$fail(expected1) {
            if (peg$currPos < peg$maxFailPos) {
                return;
            }
            if (peg$currPos > peg$maxFailPos) {
                peg$maxFailPos = peg$currPos;
                peg$maxFailExpected = [];
            }
            peg$maxFailExpected.push(expected1);
        }
        function peg$buildSimpleError(message, location1) {
            return new SyntaxError(message, [], "", location1);
        }
        function peg$buildStructuredError(expected1, found, location1) {
            return new SyntaxError(SyntaxError.buildMessage(expected1, found), expected1, found, location1);
        }
        function peg$parsestart() {
            var s0;
            s0 = peg$parsemessage();
            return s0;
        }
        function peg$parsemessage() {
            var s0, s1;
            s0 = [];
            s1 = peg$parsemessageElement();
            while (s1 !== peg$FAILED) {
                s0.push(s1);
                s1 = peg$parsemessageElement();
            }
            return s0;
        }
        function peg$parsemessageElement() {
            var s0;
            s0 = peg$parseliteralElement();
            if (s0 === peg$FAILED) {
                s0 = peg$parseargumentElement();
                if (s0 === peg$FAILED) {
                    s0 = peg$parsesimpleFormatElement();
                    if (s0 === peg$FAILED) {
                        s0 = peg$parsepluralElement();
                        if (s0 === peg$FAILED) {
                            s0 = peg$parseselectElement();
                            if (s0 === peg$FAILED) {
                                s0 = peg$parsepoundElement();
                            }
                        }
                    }
                }
            }
            return s0;
        }
        function peg$parsemessageText() {
            var s0, s1, s2;
            s0 = peg$currPos;
            s1 = [];
            s2 = peg$parsedoubleApostrophes();
            if (s2 === peg$FAILED) {
                s2 = peg$parsequotedString();
                if (s2 === peg$FAILED) {
                    s2 = peg$parseunquotedString();
                }
            }
            if (s2 !== peg$FAILED) {
                while (s2 !== peg$FAILED) {
                    s1.push(s2);
                    s2 = peg$parsedoubleApostrophes();
                    if (s2 === peg$FAILED) {
                        s2 = peg$parsequotedString();
                        if (s2 === peg$FAILED) {
                            s2 = peg$parseunquotedString();
                        }
                    }
                }
            }
            else {
                s1 = peg$FAILED;
            }
            if (s1 !== peg$FAILED) {
                peg$savedPos = s0;
                s1 = peg$c0(s1);
            }
            s0 = s1;
            return s0;
        }
        function peg$parseliteralElement() {
            var s0, s1;
            s0 = peg$currPos;
            s1 = peg$parsemessageText();
            if (s1 !== peg$FAILED) {
                peg$savedPos = s0;
                s1 = peg$c1(s1);
            }
            s0 = s1;
            return s0;
        }
        function peg$parsepoundElement() {
            var s0, s1;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 35) {
                s1 = peg$c2;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c3);
                }
            }
            if (s1 !== peg$FAILED) {
                peg$savedPos = s0;
                s1 = peg$c4();
            }
            s0 = s1;
            return s0;
        }
        function peg$parseargumentElement() {
            var s0, s1, s2, s3, s4, s5;
            peg$silentFails++;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 123) {
                s1 = peg$c6;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c7);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parse_();
                if (s2 !== peg$FAILED) {
                    s3 = peg$parseargNameOrNumber();
                    if (s3 !== peg$FAILED) {
                        s4 = peg$parse_();
                        if (s4 !== peg$FAILED) {
                            if (input.charCodeAt(peg$currPos) === 125) {
                                s5 = peg$c8;
                                peg$currPos++;
                            }
                            else {
                                s5 = peg$FAILED;
                                if (peg$silentFails === 0) {
                                    peg$fail(peg$c9);
                                }
                            }
                            if (s5 !== peg$FAILED) {
                                peg$savedPos = s0;
                                s1 = peg$c10(s3);
                                s0 = s1;
                            }
                            else {
                                peg$currPos = s0;
                                s0 = peg$FAILED;
                            }
                        }
                        else {
                            peg$currPos = s0;
                            s0 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c5);
                }
            }
            return s0;
        }
        function peg$parsenumberSkeletonId() {
            var s0, s1, s2, s3, s4;
            peg$silentFails++;
            s0 = peg$currPos;
            s1 = [];
            s2 = peg$currPos;
            s3 = peg$currPos;
            peg$silentFails++;
            s4 = peg$parsewhiteSpace();
            if (s4 === peg$FAILED) {
                if (peg$c12.test(input.charAt(peg$currPos))) {
                    s4 = input.charAt(peg$currPos);
                    peg$currPos++;
                }
                else {
                    s4 = peg$FAILED;
                    if (peg$silentFails === 0) {
                        peg$fail(peg$c13);
                    }
                }
            }
            peg$silentFails--;
            if (s4 === peg$FAILED) {
                s3 = undefined;
            }
            else {
                peg$currPos = s3;
                s3 = peg$FAILED;
            }
            if (s3 !== peg$FAILED) {
                if (input.length > peg$currPos) {
                    s4 = input.charAt(peg$currPos);
                    peg$currPos++;
                }
                else {
                    s4 = peg$FAILED;
                    if (peg$silentFails === 0) {
                        peg$fail(peg$c14);
                    }
                }
                if (s4 !== peg$FAILED) {
                    s3 = [s3, s4];
                    s2 = s3;
                }
                else {
                    peg$currPos = s2;
                    s2 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s2;
                s2 = peg$FAILED;
            }
            if (s2 !== peg$FAILED) {
                while (s2 !== peg$FAILED) {
                    s1.push(s2);
                    s2 = peg$currPos;
                    s3 = peg$currPos;
                    peg$silentFails++;
                    s4 = peg$parsewhiteSpace();
                    if (s4 === peg$FAILED) {
                        if (peg$c12.test(input.charAt(peg$currPos))) {
                            s4 = input.charAt(peg$currPos);
                            peg$currPos++;
                        }
                        else {
                            s4 = peg$FAILED;
                            if (peg$silentFails === 0) {
                                peg$fail(peg$c13);
                            }
                        }
                    }
                    peg$silentFails--;
                    if (s4 === peg$FAILED) {
                        s3 = undefined;
                    }
                    else {
                        peg$currPos = s3;
                        s3 = peg$FAILED;
                    }
                    if (s3 !== peg$FAILED) {
                        if (input.length > peg$currPos) {
                            s4 = input.charAt(peg$currPos);
                            peg$currPos++;
                        }
                        else {
                            s4 = peg$FAILED;
                            if (peg$silentFails === 0) {
                                peg$fail(peg$c14);
                            }
                        }
                        if (s4 !== peg$FAILED) {
                            s3 = [s3, s4];
                            s2 = s3;
                        }
                        else {
                            peg$currPos = s2;
                            s2 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s2;
                        s2 = peg$FAILED;
                    }
                }
            }
            else {
                s1 = peg$FAILED;
            }
            if (s1 !== peg$FAILED) {
                s0 = input.substring(s0, peg$currPos);
            }
            else {
                s0 = s1;
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c11);
                }
            }
            return s0;
        }
        function peg$parsenumberSkeletonTokenOption() {
            var s0, s1, s2;
            peg$silentFails++;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 47) {
                s1 = peg$c16;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c17);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parsenumberSkeletonId();
                if (s2 !== peg$FAILED) {
                    peg$savedPos = s0;
                    s1 = peg$c18(s2);
                    s0 = s1;
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c15);
                }
            }
            return s0;
        }
        function peg$parsenumberSkeletonToken() {
            var s0, s1, s2, s3, s4;
            peg$silentFails++;
            s0 = peg$currPos;
            s1 = peg$parse_();
            if (s1 !== peg$FAILED) {
                s2 = peg$parsenumberSkeletonId();
                if (s2 !== peg$FAILED) {
                    s3 = [];
                    s4 = peg$parsenumberSkeletonTokenOption();
                    while (s4 !== peg$FAILED) {
                        s3.push(s4);
                        s4 = peg$parsenumberSkeletonTokenOption();
                    }
                    if (s3 !== peg$FAILED) {
                        peg$savedPos = s0;
                        s1 = peg$c20(s2, s3);
                        s0 = s1;
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c19);
                }
            }
            return s0;
        }
        function peg$parsenumberSkeleton() {
            var s0, s1, s2;
            s0 = peg$currPos;
            s1 = [];
            s2 = peg$parsenumberSkeletonToken();
            if (s2 !== peg$FAILED) {
                while (s2 !== peg$FAILED) {
                    s1.push(s2);
                    s2 = peg$parsenumberSkeletonToken();
                }
            }
            else {
                s1 = peg$FAILED;
            }
            if (s1 !== peg$FAILED) {
                peg$savedPos = s0;
                s1 = peg$c21(s1);
            }
            s0 = s1;
            return s0;
        }
        function peg$parsenumberArgStyle() {
            var s0, s1, s2;
            s0 = peg$currPos;
            if (input.substr(peg$currPos, 2) === peg$c22) {
                s1 = peg$c22;
                peg$currPos += 2;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c23);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parsenumberSkeleton();
                if (s2 !== peg$FAILED) {
                    peg$savedPos = s0;
                    s1 = peg$c24(s2);
                    s0 = s1;
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            if (s0 === peg$FAILED) {
                s0 = peg$currPos;
                peg$savedPos = peg$currPos;
                s1 = peg$c25();
                if (s1) {
                    s1 = undefined;
                }
                else {
                    s1 = peg$FAILED;
                }
                if (s1 !== peg$FAILED) {
                    s2 = peg$parsemessageText();
                    if (s2 !== peg$FAILED) {
                        peg$savedPos = s0;
                        s1 = peg$c26(s2);
                        s0 = s1;
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            return s0;
        }
        function peg$parsenumberFormatElement() {
            var s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 123) {
                s1 = peg$c6;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c7);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parse_();
                if (s2 !== peg$FAILED) {
                    s3 = peg$parseargNameOrNumber();
                    if (s3 !== peg$FAILED) {
                        s4 = peg$parse_();
                        if (s4 !== peg$FAILED) {
                            if (input.charCodeAt(peg$currPos) === 44) {
                                s5 = peg$c27;
                                peg$currPos++;
                            }
                            else {
                                s5 = peg$FAILED;
                                if (peg$silentFails === 0) {
                                    peg$fail(peg$c28);
                                }
                            }
                            if (s5 !== peg$FAILED) {
                                s6 = peg$parse_();
                                if (s6 !== peg$FAILED) {
                                    if (input.substr(peg$currPos, 6) === peg$c29) {
                                        s7 = peg$c29;
                                        peg$currPos += 6;
                                    }
                                    else {
                                        s7 = peg$FAILED;
                                        if (peg$silentFails === 0) {
                                            peg$fail(peg$c30);
                                        }
                                    }
                                    if (s7 !== peg$FAILED) {
                                        s8 = peg$parse_();
                                        if (s8 !== peg$FAILED) {
                                            s9 = peg$currPos;
                                            if (input.charCodeAt(peg$currPos) === 44) {
                                                s10 = peg$c27;
                                                peg$currPos++;
                                            }
                                            else {
                                                s10 = peg$FAILED;
                                                if (peg$silentFails === 0) {
                                                    peg$fail(peg$c28);
                                                }
                                            }
                                            if (s10 !== peg$FAILED) {
                                                s11 = peg$parse_();
                                                if (s11 !== peg$FAILED) {
                                                    s12 = peg$parsenumberArgStyle();
                                                    if (s12 !== peg$FAILED) {
                                                        s10 = [s10, s11, s12];
                                                        s9 = s10;
                                                    }
                                                    else {
                                                        peg$currPos = s9;
                                                        s9 = peg$FAILED;
                                                    }
                                                }
                                                else {
                                                    peg$currPos = s9;
                                                    s9 = peg$FAILED;
                                                }
                                            }
                                            else {
                                                peg$currPos = s9;
                                                s9 = peg$FAILED;
                                            }
                                            if (s9 === peg$FAILED) {
                                                s9 = null;
                                            }
                                            if (s9 !== peg$FAILED) {
                                                s10 = peg$parse_();
                                                if (s10 !== peg$FAILED) {
                                                    if (input.charCodeAt(peg$currPos) === 125) {
                                                        s11 = peg$c8;
                                                        peg$currPos++;
                                                    }
                                                    else {
                                                        s11 = peg$FAILED;
                                                        if (peg$silentFails === 0) {
                                                            peg$fail(peg$c9);
                                                        }
                                                    }
                                                    if (s11 !== peg$FAILED) {
                                                        peg$savedPos = s0;
                                                        s1 = peg$c31(s3, s7, s9);
                                                        s0 = s1;
                                                    }
                                                    else {
                                                        peg$currPos = s0;
                                                        s0 = peg$FAILED;
                                                    }
                                                }
                                                else {
                                                    peg$currPos = s0;
                                                    s0 = peg$FAILED;
                                                }
                                            }
                                            else {
                                                peg$currPos = s0;
                                                s0 = peg$FAILED;
                                            }
                                        }
                                        else {
                                            peg$currPos = s0;
                                            s0 = peg$FAILED;
                                        }
                                    }
                                    else {
                                        peg$currPos = s0;
                                        s0 = peg$FAILED;
                                    }
                                }
                                else {
                                    peg$currPos = s0;
                                    s0 = peg$FAILED;
                                }
                            }
                            else {
                                peg$currPos = s0;
                                s0 = peg$FAILED;
                            }
                        }
                        else {
                            peg$currPos = s0;
                            s0 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            return s0;
        }
        function peg$parsedateTimeSkeletonLiteral() {
            var s0, s1, s2, s3;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 39) {
                s1 = peg$c32;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c33);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = [];
                s3 = peg$parsedoubleApostrophes();
                if (s3 === peg$FAILED) {
                    if (peg$c34.test(input.charAt(peg$currPos))) {
                        s3 = input.charAt(peg$currPos);
                        peg$currPos++;
                    }
                    else {
                        s3 = peg$FAILED;
                        if (peg$silentFails === 0) {
                            peg$fail(peg$c35);
                        }
                    }
                }
                if (s3 !== peg$FAILED) {
                    while (s3 !== peg$FAILED) {
                        s2.push(s3);
                        s3 = peg$parsedoubleApostrophes();
                        if (s3 === peg$FAILED) {
                            if (peg$c34.test(input.charAt(peg$currPos))) {
                                s3 = input.charAt(peg$currPos);
                                peg$currPos++;
                            }
                            else {
                                s3 = peg$FAILED;
                                if (peg$silentFails === 0) {
                                    peg$fail(peg$c35);
                                }
                            }
                        }
                    }
                }
                else {
                    s2 = peg$FAILED;
                }
                if (s2 !== peg$FAILED) {
                    if (input.charCodeAt(peg$currPos) === 39) {
                        s3 = peg$c32;
                        peg$currPos++;
                    }
                    else {
                        s3 = peg$FAILED;
                        if (peg$silentFails === 0) {
                            peg$fail(peg$c33);
                        }
                    }
                    if (s3 !== peg$FAILED) {
                        s1 = [s1, s2, s3];
                        s0 = s1;
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            if (s0 === peg$FAILED) {
                s0 = [];
                s1 = peg$parsedoubleApostrophes();
                if (s1 === peg$FAILED) {
                    if (peg$c36.test(input.charAt(peg$currPos))) {
                        s1 = input.charAt(peg$currPos);
                        peg$currPos++;
                    }
                    else {
                        s1 = peg$FAILED;
                        if (peg$silentFails === 0) {
                            peg$fail(peg$c37);
                        }
                    }
                }
                if (s1 !== peg$FAILED) {
                    while (s1 !== peg$FAILED) {
                        s0.push(s1);
                        s1 = peg$parsedoubleApostrophes();
                        if (s1 === peg$FAILED) {
                            if (peg$c36.test(input.charAt(peg$currPos))) {
                                s1 = input.charAt(peg$currPos);
                                peg$currPos++;
                            }
                            else {
                                s1 = peg$FAILED;
                                if (peg$silentFails === 0) {
                                    peg$fail(peg$c37);
                                }
                            }
                        }
                    }
                }
                else {
                    s0 = peg$FAILED;
                }
            }
            return s0;
        }
        function peg$parsedateTimeSkeletonPattern() {
            var s0, s1;
            s0 = [];
            if (peg$c38.test(input.charAt(peg$currPos))) {
                s1 = input.charAt(peg$currPos);
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c39);
                }
            }
            if (s1 !== peg$FAILED) {
                while (s1 !== peg$FAILED) {
                    s0.push(s1);
                    if (peg$c38.test(input.charAt(peg$currPos))) {
                        s1 = input.charAt(peg$currPos);
                        peg$currPos++;
                    }
                    else {
                        s1 = peg$FAILED;
                        if (peg$silentFails === 0) {
                            peg$fail(peg$c39);
                        }
                    }
                }
            }
            else {
                s0 = peg$FAILED;
            }
            return s0;
        }
        function peg$parsedateTimeSkeleton() {
            var s0, s1, s2, s3;
            s0 = peg$currPos;
            s1 = peg$currPos;
            s2 = [];
            s3 = peg$parsedateTimeSkeletonLiteral();
            if (s3 === peg$FAILED) {
                s3 = peg$parsedateTimeSkeletonPattern();
            }
            if (s3 !== peg$FAILED) {
                while (s3 !== peg$FAILED) {
                    s2.push(s3);
                    s3 = peg$parsedateTimeSkeletonLiteral();
                    if (s3 === peg$FAILED) {
                        s3 = peg$parsedateTimeSkeletonPattern();
                    }
                }
            }
            else {
                s2 = peg$FAILED;
            }
            if (s2 !== peg$FAILED) {
                s1 = input.substring(s1, peg$currPos);
            }
            else {
                s1 = s2;
            }
            if (s1 !== peg$FAILED) {
                peg$savedPos = s0;
                s1 = peg$c40(s1);
            }
            s0 = s1;
            return s0;
        }
        function peg$parsedateOrTimeArgStyle() {
            var s0, s1, s2;
            s0 = peg$currPos;
            if (input.substr(peg$currPos, 2) === peg$c22) {
                s1 = peg$c22;
                peg$currPos += 2;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c23);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parsedateTimeSkeleton();
                if (s2 !== peg$FAILED) {
                    peg$savedPos = s0;
                    s1 = peg$c24(s2);
                    s0 = s1;
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            if (s0 === peg$FAILED) {
                s0 = peg$currPos;
                peg$savedPos = peg$currPos;
                s1 = peg$c41();
                if (s1) {
                    s1 = undefined;
                }
                else {
                    s1 = peg$FAILED;
                }
                if (s1 !== peg$FAILED) {
                    s2 = peg$parsemessageText();
                    if (s2 !== peg$FAILED) {
                        peg$savedPos = s0;
                        s1 = peg$c26(s2);
                        s0 = s1;
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            return s0;
        }
        function peg$parsedateOrTimeFormatElement() {
            var s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 123) {
                s1 = peg$c6;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c7);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parse_();
                if (s2 !== peg$FAILED) {
                    s3 = peg$parseargNameOrNumber();
                    if (s3 !== peg$FAILED) {
                        s4 = peg$parse_();
                        if (s4 !== peg$FAILED) {
                            if (input.charCodeAt(peg$currPos) === 44) {
                                s5 = peg$c27;
                                peg$currPos++;
                            }
                            else {
                                s5 = peg$FAILED;
                                if (peg$silentFails === 0) {
                                    peg$fail(peg$c28);
                                }
                            }
                            if (s5 !== peg$FAILED) {
                                s6 = peg$parse_();
                                if (s6 !== peg$FAILED) {
                                    if (input.substr(peg$currPos, 4) === peg$c42) {
                                        s7 = peg$c42;
                                        peg$currPos += 4;
                                    }
                                    else {
                                        s7 = peg$FAILED;
                                        if (peg$silentFails === 0) {
                                            peg$fail(peg$c43);
                                        }
                                    }
                                    if (s7 === peg$FAILED) {
                                        if (input.substr(peg$currPos, 4) === peg$c44) {
                                            s7 = peg$c44;
                                            peg$currPos += 4;
                                        }
                                        else {
                                            s7 = peg$FAILED;
                                            if (peg$silentFails === 0) {
                                                peg$fail(peg$c45);
                                            }
                                        }
                                    }
                                    if (s7 !== peg$FAILED) {
                                        s8 = peg$parse_();
                                        if (s8 !== peg$FAILED) {
                                            s9 = peg$currPos;
                                            if (input.charCodeAt(peg$currPos) === 44) {
                                                s10 = peg$c27;
                                                peg$currPos++;
                                            }
                                            else {
                                                s10 = peg$FAILED;
                                                if (peg$silentFails === 0) {
                                                    peg$fail(peg$c28);
                                                }
                                            }
                                            if (s10 !== peg$FAILED) {
                                                s11 = peg$parse_();
                                                if (s11 !== peg$FAILED) {
                                                    s12 = peg$parsedateOrTimeArgStyle();
                                                    if (s12 !== peg$FAILED) {
                                                        s10 = [s10, s11, s12];
                                                        s9 = s10;
                                                    }
                                                    else {
                                                        peg$currPos = s9;
                                                        s9 = peg$FAILED;
                                                    }
                                                }
                                                else {
                                                    peg$currPos = s9;
                                                    s9 = peg$FAILED;
                                                }
                                            }
                                            else {
                                                peg$currPos = s9;
                                                s9 = peg$FAILED;
                                            }
                                            if (s9 === peg$FAILED) {
                                                s9 = null;
                                            }
                                            if (s9 !== peg$FAILED) {
                                                s10 = peg$parse_();
                                                if (s10 !== peg$FAILED) {
                                                    if (input.charCodeAt(peg$currPos) === 125) {
                                                        s11 = peg$c8;
                                                        peg$currPos++;
                                                    }
                                                    else {
                                                        s11 = peg$FAILED;
                                                        if (peg$silentFails === 0) {
                                                            peg$fail(peg$c9);
                                                        }
                                                    }
                                                    if (s11 !== peg$FAILED) {
                                                        peg$savedPos = s0;
                                                        s1 = peg$c31(s3, s7, s9);
                                                        s0 = s1;
                                                    }
                                                    else {
                                                        peg$currPos = s0;
                                                        s0 = peg$FAILED;
                                                    }
                                                }
                                                else {
                                                    peg$currPos = s0;
                                                    s0 = peg$FAILED;
                                                }
                                            }
                                            else {
                                                peg$currPos = s0;
                                                s0 = peg$FAILED;
                                            }
                                        }
                                        else {
                                            peg$currPos = s0;
                                            s0 = peg$FAILED;
                                        }
                                    }
                                    else {
                                        peg$currPos = s0;
                                        s0 = peg$FAILED;
                                    }
                                }
                                else {
                                    peg$currPos = s0;
                                    s0 = peg$FAILED;
                                }
                            }
                            else {
                                peg$currPos = s0;
                                s0 = peg$FAILED;
                            }
                        }
                        else {
                            peg$currPos = s0;
                            s0 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            return s0;
        }
        function peg$parsesimpleFormatElement() {
            var s0;
            s0 = peg$parsenumberFormatElement();
            if (s0 === peg$FAILED) {
                s0 = peg$parsedateOrTimeFormatElement();
            }
            return s0;
        }
        function peg$parsepluralElement() {
            var s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 123) {
                s1 = peg$c6;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c7);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parse_();
                if (s2 !== peg$FAILED) {
                    s3 = peg$parseargNameOrNumber();
                    if (s3 !== peg$FAILED) {
                        s4 = peg$parse_();
                        if (s4 !== peg$FAILED) {
                            if (input.charCodeAt(peg$currPos) === 44) {
                                s5 = peg$c27;
                                peg$currPos++;
                            }
                            else {
                                s5 = peg$FAILED;
                                if (peg$silentFails === 0) {
                                    peg$fail(peg$c28);
                                }
                            }
                            if (s5 !== peg$FAILED) {
                                s6 = peg$parse_();
                                if (s6 !== peg$FAILED) {
                                    if (input.substr(peg$currPos, 6) === peg$c46) {
                                        s7 = peg$c46;
                                        peg$currPos += 6;
                                    }
                                    else {
                                        s7 = peg$FAILED;
                                        if (peg$silentFails === 0) {
                                            peg$fail(peg$c47);
                                        }
                                    }
                                    if (s7 === peg$FAILED) {
                                        if (input.substr(peg$currPos, 13) === peg$c48) {
                                            s7 = peg$c48;
                                            peg$currPos += 13;
                                        }
                                        else {
                                            s7 = peg$FAILED;
                                            if (peg$silentFails === 0) {
                                                peg$fail(peg$c49);
                                            }
                                        }
                                    }
                                    if (s7 !== peg$FAILED) {
                                        s8 = peg$parse_();
                                        if (s8 !== peg$FAILED) {
                                            if (input.charCodeAt(peg$currPos) === 44) {
                                                s9 = peg$c27;
                                                peg$currPos++;
                                            }
                                            else {
                                                s9 = peg$FAILED;
                                                if (peg$silentFails === 0) {
                                                    peg$fail(peg$c28);
                                                }
                                            }
                                            if (s9 !== peg$FAILED) {
                                                s10 = peg$parse_();
                                                if (s10 !== peg$FAILED) {
                                                    s11 = peg$currPos;
                                                    if (input.substr(peg$currPos, 7) === peg$c50) {
                                                        s12 = peg$c50;
                                                        peg$currPos += 7;
                                                    }
                                                    else {
                                                        s12 = peg$FAILED;
                                                        if (peg$silentFails === 0) {
                                                            peg$fail(peg$c51);
                                                        }
                                                    }
                                                    if (s12 !== peg$FAILED) {
                                                        s13 = peg$parse_();
                                                        if (s13 !== peg$FAILED) {
                                                            s14 = peg$parsenumber();
                                                            if (s14 !== peg$FAILED) {
                                                                s12 = [s12, s13, s14];
                                                                s11 = s12;
                                                            }
                                                            else {
                                                                peg$currPos = s11;
                                                                s11 = peg$FAILED;
                                                            }
                                                        }
                                                        else {
                                                            peg$currPos = s11;
                                                            s11 = peg$FAILED;
                                                        }
                                                    }
                                                    else {
                                                        peg$currPos = s11;
                                                        s11 = peg$FAILED;
                                                    }
                                                    if (s11 === peg$FAILED) {
                                                        s11 = null;
                                                    }
                                                    if (s11 !== peg$FAILED) {
                                                        s12 = peg$parse_();
                                                        if (s12 !== peg$FAILED) {
                                                            s13 = [];
                                                            s14 = peg$parsepluralOption();
                                                            if (s14 !== peg$FAILED) {
                                                                while (s14 !== peg$FAILED) {
                                                                    s13.push(s14);
                                                                    s14 = peg$parsepluralOption();
                                                                }
                                                            }
                                                            else {
                                                                s13 = peg$FAILED;
                                                            }
                                                            if (s13 !== peg$FAILED) {
                                                                s14 = peg$parse_();
                                                                if (s14 !== peg$FAILED) {
                                                                    if (input.charCodeAt(peg$currPos) === 125) {
                                                                        s15 = peg$c8;
                                                                        peg$currPos++;
                                                                    }
                                                                    else {
                                                                        s15 = peg$FAILED;
                                                                        if (peg$silentFails === 0) {
                                                                            peg$fail(peg$c9);
                                                                        }
                                                                    }
                                                                    if (s15 !== peg$FAILED) {
                                                                        peg$savedPos = s0;
                                                                        s1 = peg$c52(s3, s7, s11, s13);
                                                                        s0 = s1;
                                                                    }
                                                                    else {
                                                                        peg$currPos = s0;
                                                                        s0 = peg$FAILED;
                                                                    }
                                                                }
                                                                else {
                                                                    peg$currPos = s0;
                                                                    s0 = peg$FAILED;
                                                                }
                                                            }
                                                            else {
                                                                peg$currPos = s0;
                                                                s0 = peg$FAILED;
                                                            }
                                                        }
                                                        else {
                                                            peg$currPos = s0;
                                                            s0 = peg$FAILED;
                                                        }
                                                    }
                                                    else {
                                                        peg$currPos = s0;
                                                        s0 = peg$FAILED;
                                                    }
                                                }
                                                else {
                                                    peg$currPos = s0;
                                                    s0 = peg$FAILED;
                                                }
                                            }
                                            else {
                                                peg$currPos = s0;
                                                s0 = peg$FAILED;
                                            }
                                        }
                                        else {
                                            peg$currPos = s0;
                                            s0 = peg$FAILED;
                                        }
                                    }
                                    else {
                                        peg$currPos = s0;
                                        s0 = peg$FAILED;
                                    }
                                }
                                else {
                                    peg$currPos = s0;
                                    s0 = peg$FAILED;
                                }
                            }
                            else {
                                peg$currPos = s0;
                                s0 = peg$FAILED;
                            }
                        }
                        else {
                            peg$currPos = s0;
                            s0 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            return s0;
        }
        function peg$parseselectElement() {
            var s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 123) {
                s1 = peg$c6;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c7);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parse_();
                if (s2 !== peg$FAILED) {
                    s3 = peg$parseargNameOrNumber();
                    if (s3 !== peg$FAILED) {
                        s4 = peg$parse_();
                        if (s4 !== peg$FAILED) {
                            if (input.charCodeAt(peg$currPos) === 44) {
                                s5 = peg$c27;
                                peg$currPos++;
                            }
                            else {
                                s5 = peg$FAILED;
                                if (peg$silentFails === 0) {
                                    peg$fail(peg$c28);
                                }
                            }
                            if (s5 !== peg$FAILED) {
                                s6 = peg$parse_();
                                if (s6 !== peg$FAILED) {
                                    if (input.substr(peg$currPos, 6) === peg$c53) {
                                        s7 = peg$c53;
                                        peg$currPos += 6;
                                    }
                                    else {
                                        s7 = peg$FAILED;
                                        if (peg$silentFails === 0) {
                                            peg$fail(peg$c54);
                                        }
                                    }
                                    if (s7 !== peg$FAILED) {
                                        s8 = peg$parse_();
                                        if (s8 !== peg$FAILED) {
                                            if (input.charCodeAt(peg$currPos) === 44) {
                                                s9 = peg$c27;
                                                peg$currPos++;
                                            }
                                            else {
                                                s9 = peg$FAILED;
                                                if (peg$silentFails === 0) {
                                                    peg$fail(peg$c28);
                                                }
                                            }
                                            if (s9 !== peg$FAILED) {
                                                s10 = peg$parse_();
                                                if (s10 !== peg$FAILED) {
                                                    s11 = [];
                                                    s12 = peg$parseselectOption();
                                                    if (s12 !== peg$FAILED) {
                                                        while (s12 !== peg$FAILED) {
                                                            s11.push(s12);
                                                            s12 = peg$parseselectOption();
                                                        }
                                                    }
                                                    else {
                                                        s11 = peg$FAILED;
                                                    }
                                                    if (s11 !== peg$FAILED) {
                                                        s12 = peg$parse_();
                                                        if (s12 !== peg$FAILED) {
                                                            if (input.charCodeAt(peg$currPos) === 125) {
                                                                s13 = peg$c8;
                                                                peg$currPos++;
                                                            }
                                                            else {
                                                                s13 = peg$FAILED;
                                                                if (peg$silentFails === 0) {
                                                                    peg$fail(peg$c9);
                                                                }
                                                            }
                                                            if (s13 !== peg$FAILED) {
                                                                peg$savedPos = s0;
                                                                s1 = peg$c55(s3, s11);
                                                                s0 = s1;
                                                            }
                                                            else {
                                                                peg$currPos = s0;
                                                                s0 = peg$FAILED;
                                                            }
                                                        }
                                                        else {
                                                            peg$currPos = s0;
                                                            s0 = peg$FAILED;
                                                        }
                                                    }
                                                    else {
                                                        peg$currPos = s0;
                                                        s0 = peg$FAILED;
                                                    }
                                                }
                                                else {
                                                    peg$currPos = s0;
                                                    s0 = peg$FAILED;
                                                }
                                            }
                                            else {
                                                peg$currPos = s0;
                                                s0 = peg$FAILED;
                                            }
                                        }
                                        else {
                                            peg$currPos = s0;
                                            s0 = peg$FAILED;
                                        }
                                    }
                                    else {
                                        peg$currPos = s0;
                                        s0 = peg$FAILED;
                                    }
                                }
                                else {
                                    peg$currPos = s0;
                                    s0 = peg$FAILED;
                                }
                            }
                            else {
                                peg$currPos = s0;
                                s0 = peg$FAILED;
                            }
                        }
                        else {
                            peg$currPos = s0;
                            s0 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            return s0;
        }
        function peg$parsepluralRuleSelectValue() {
            var s0, s1, s2, s3;
            s0 = peg$currPos;
            s1 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 61) {
                s2 = peg$c56;
                peg$currPos++;
            }
            else {
                s2 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c57);
                }
            }
            if (s2 !== peg$FAILED) {
                s3 = peg$parsenumber();
                if (s3 !== peg$FAILED) {
                    s2 = [s2, s3];
                    s1 = s2;
                }
                else {
                    peg$currPos = s1;
                    s1 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s1;
                s1 = peg$FAILED;
            }
            if (s1 !== peg$FAILED) {
                s0 = input.substring(s0, peg$currPos);
            }
            else {
                s0 = s1;
            }
            if (s0 === peg$FAILED) {
                s0 = peg$parseargName();
            }
            return s0;
        }
        function peg$parseselectOption() {
            var s0, s1, s2, s3, s4, s5, s6, s7;
            s0 = peg$currPos;
            s1 = peg$parse_();
            if (s1 !== peg$FAILED) {
                s2 = peg$parseargName();
                if (s2 !== peg$FAILED) {
                    s3 = peg$parse_();
                    if (s3 !== peg$FAILED) {
                        if (input.charCodeAt(peg$currPos) === 123) {
                            s4 = peg$c6;
                            peg$currPos++;
                        }
                        else {
                            s4 = peg$FAILED;
                            if (peg$silentFails === 0) {
                                peg$fail(peg$c7);
                            }
                        }
                        if (s4 !== peg$FAILED) {
                            peg$savedPos = peg$currPos;
                            s5 = peg$c58();
                            if (s5) {
                                s5 = undefined;
                            }
                            else {
                                s5 = peg$FAILED;
                            }
                            if (s5 !== peg$FAILED) {
                                s6 = peg$parsemessage();
                                if (s6 !== peg$FAILED) {
                                    if (input.charCodeAt(peg$currPos) === 125) {
                                        s7 = peg$c8;
                                        peg$currPos++;
                                    }
                                    else {
                                        s7 = peg$FAILED;
                                        if (peg$silentFails === 0) {
                                            peg$fail(peg$c9);
                                        }
                                    }
                                    if (s7 !== peg$FAILED) {
                                        peg$savedPos = s0;
                                        s1 = peg$c59(s2, s6);
                                        s0 = s1;
                                    }
                                    else {
                                        peg$currPos = s0;
                                        s0 = peg$FAILED;
                                    }
                                }
                                else {
                                    peg$currPos = s0;
                                    s0 = peg$FAILED;
                                }
                            }
                            else {
                                peg$currPos = s0;
                                s0 = peg$FAILED;
                            }
                        }
                        else {
                            peg$currPos = s0;
                            s0 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            return s0;
        }
        function peg$parsepluralOption() {
            var s0, s1, s2, s3, s4, s5, s6, s7;
            s0 = peg$currPos;
            s1 = peg$parse_();
            if (s1 !== peg$FAILED) {
                s2 = peg$parsepluralRuleSelectValue();
                if (s2 !== peg$FAILED) {
                    s3 = peg$parse_();
                    if (s3 !== peg$FAILED) {
                        if (input.charCodeAt(peg$currPos) === 123) {
                            s4 = peg$c6;
                            peg$currPos++;
                        }
                        else {
                            s4 = peg$FAILED;
                            if (peg$silentFails === 0) {
                                peg$fail(peg$c7);
                            }
                        }
                        if (s4 !== peg$FAILED) {
                            peg$savedPos = peg$currPos;
                            s5 = peg$c60();
                            if (s5) {
                                s5 = undefined;
                            }
                            else {
                                s5 = peg$FAILED;
                            }
                            if (s5 !== peg$FAILED) {
                                s6 = peg$parsemessage();
                                if (s6 !== peg$FAILED) {
                                    if (input.charCodeAt(peg$currPos) === 125) {
                                        s7 = peg$c8;
                                        peg$currPos++;
                                    }
                                    else {
                                        s7 = peg$FAILED;
                                        if (peg$silentFails === 0) {
                                            peg$fail(peg$c9);
                                        }
                                    }
                                    if (s7 !== peg$FAILED) {
                                        peg$savedPos = s0;
                                        s1 = peg$c61(s2, s6);
                                        s0 = s1;
                                    }
                                    else {
                                        peg$currPos = s0;
                                        s0 = peg$FAILED;
                                    }
                                }
                                else {
                                    peg$currPos = s0;
                                    s0 = peg$FAILED;
                                }
                            }
                            else {
                                peg$currPos = s0;
                                s0 = peg$FAILED;
                            }
                        }
                        else {
                            peg$currPos = s0;
                            s0 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            return s0;
        }
        function peg$parsewhiteSpace() {
            var s0;
            peg$silentFails++;
            if (peg$c63.test(input.charAt(peg$currPos))) {
                s0 = input.charAt(peg$currPos);
                peg$currPos++;
            }
            else {
                s0 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c64);
                }
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                if (peg$silentFails === 0) {
                    peg$fail(peg$c62);
                }
            }
            return s0;
        }
        function peg$parsepatternSyntax() {
            var s0;
            peg$silentFails++;
            if (peg$c66.test(input.charAt(peg$currPos))) {
                s0 = input.charAt(peg$currPos);
                peg$currPos++;
            }
            else {
                s0 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c67);
                }
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                if (peg$silentFails === 0) {
                    peg$fail(peg$c65);
                }
            }
            return s0;
        }
        function peg$parse_() {
            var s0, s1, s2;
            peg$silentFails++;
            s0 = peg$currPos;
            s1 = [];
            s2 = peg$parsewhiteSpace();
            while (s2 !== peg$FAILED) {
                s1.push(s2);
                s2 = peg$parsewhiteSpace();
            }
            if (s1 !== peg$FAILED) {
                s0 = input.substring(s0, peg$currPos);
            }
            else {
                s0 = s1;
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c68);
                }
            }
            return s0;
        }
        function peg$parsenumber() {
            var s0, s1, s2;
            peg$silentFails++;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 45) {
                s1 = peg$c70;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c71);
                }
            }
            if (s1 === peg$FAILED) {
                s1 = null;
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parseargNumber();
                if (s2 !== peg$FAILED) {
                    peg$savedPos = s0;
                    s1 = peg$c72(s1, s2);
                    s0 = s1;
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c69);
                }
            }
            return s0;
        }
        function peg$parsedoubleApostrophes() {
            var s0, s1;
            peg$silentFails++;
            s0 = peg$currPos;
            if (input.substr(peg$currPos, 2) === peg$c75) {
                s1 = peg$c75;
                peg$currPos += 2;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c76);
                }
            }
            if (s1 !== peg$FAILED) {
                peg$savedPos = s0;
                s1 = peg$c77();
            }
            s0 = s1;
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c74);
                }
            }
            return s0;
        }
        function peg$parsequotedString() {
            var s0, s1, s2, s3, s4, s5;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 39) {
                s1 = peg$c32;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c33);
                }
            }
            if (s1 !== peg$FAILED) {
                s2 = peg$parseescapedChar();
                if (s2 !== peg$FAILED) {
                    s3 = peg$currPos;
                    s4 = [];
                    if (input.substr(peg$currPos, 2) === peg$c75) {
                        s5 = peg$c75;
                        peg$currPos += 2;
                    }
                    else {
                        s5 = peg$FAILED;
                        if (peg$silentFails === 0) {
                            peg$fail(peg$c76);
                        }
                    }
                    if (s5 === peg$FAILED) {
                        if (peg$c34.test(input.charAt(peg$currPos))) {
                            s5 = input.charAt(peg$currPos);
                            peg$currPos++;
                        }
                        else {
                            s5 = peg$FAILED;
                            if (peg$silentFails === 0) {
                                peg$fail(peg$c35);
                            }
                        }
                    }
                    while (s5 !== peg$FAILED) {
                        s4.push(s5);
                        if (input.substr(peg$currPos, 2) === peg$c75) {
                            s5 = peg$c75;
                            peg$currPos += 2;
                        }
                        else {
                            s5 = peg$FAILED;
                            if (peg$silentFails === 0) {
                                peg$fail(peg$c76);
                            }
                        }
                        if (s5 === peg$FAILED) {
                            if (peg$c34.test(input.charAt(peg$currPos))) {
                                s5 = input.charAt(peg$currPos);
                                peg$currPos++;
                            }
                            else {
                                s5 = peg$FAILED;
                                if (peg$silentFails === 0) {
                                    peg$fail(peg$c35);
                                }
                            }
                        }
                    }
                    if (s4 !== peg$FAILED) {
                        s3 = input.substring(s3, peg$currPos);
                    }
                    else {
                        s3 = s4;
                    }
                    if (s3 !== peg$FAILED) {
                        if (input.charCodeAt(peg$currPos) === 39) {
                            s4 = peg$c32;
                            peg$currPos++;
                        }
                        else {
                            s4 = peg$FAILED;
                            if (peg$silentFails === 0) {
                                peg$fail(peg$c33);
                            }
                        }
                        if (s4 === peg$FAILED) {
                            s4 = null;
                        }
                        if (s4 !== peg$FAILED) {
                            peg$savedPos = s0;
                            s1 = peg$c78(s2, s3);
                            s0 = s1;
                        }
                        else {
                            peg$currPos = s0;
                            s0 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s0;
                s0 = peg$FAILED;
            }
            return s0;
        }
        function peg$parseunquotedString() {
            var s0, s1, s2, s3;
            s0 = peg$currPos;
            s1 = peg$currPos;
            if (input.length > peg$currPos) {
                s2 = input.charAt(peg$currPos);
                peg$currPos++;
            }
            else {
                s2 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c14);
                }
            }
            if (s2 !== peg$FAILED) {
                peg$savedPos = peg$currPos;
                s3 = peg$c79(s2);
                if (s3) {
                    s3 = undefined;
                }
                else {
                    s3 = peg$FAILED;
                }
                if (s3 !== peg$FAILED) {
                    s2 = [s2, s3];
                    s1 = s2;
                }
                else {
                    peg$currPos = s1;
                    s1 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s1;
                s1 = peg$FAILED;
            }
            if (s1 === peg$FAILED) {
                if (input.charCodeAt(peg$currPos) === 10) {
                    s1 = peg$c80;
                    peg$currPos++;
                }
                else {
                    s1 = peg$FAILED;
                    if (peg$silentFails === 0) {
                        peg$fail(peg$c81);
                    }
                }
            }
            if (s1 !== peg$FAILED) {
                s0 = input.substring(s0, peg$currPos);
            }
            else {
                s0 = s1;
            }
            return s0;
        }
        function peg$parseescapedChar() {
            var s0, s1, s2, s3;
            s0 = peg$currPos;
            s1 = peg$currPos;
            if (input.length > peg$currPos) {
                s2 = input.charAt(peg$currPos);
                peg$currPos++;
            }
            else {
                s2 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c14);
                }
            }
            if (s2 !== peg$FAILED) {
                peg$savedPos = peg$currPos;
                s3 = peg$c82(s2);
                if (s3) {
                    s3 = undefined;
                }
                else {
                    s3 = peg$FAILED;
                }
                if (s3 !== peg$FAILED) {
                    s2 = [s2, s3];
                    s1 = s2;
                }
                else {
                    peg$currPos = s1;
                    s1 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s1;
                s1 = peg$FAILED;
            }
            if (s1 !== peg$FAILED) {
                s0 = input.substring(s0, peg$currPos);
            }
            else {
                s0 = s1;
            }
            return s0;
        }
        function peg$parseargNameOrNumber() {
            var s0, s1;
            peg$silentFails++;
            s0 = peg$currPos;
            s1 = peg$parseargNumber();
            if (s1 === peg$FAILED) {
                s1 = peg$parseargName();
            }
            if (s1 !== peg$FAILED) {
                s0 = input.substring(s0, peg$currPos);
            }
            else {
                s0 = s1;
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c83);
                }
            }
            return s0;
        }
        function peg$parseargNumber() {
            var s0, s1, s2, s3, s4;
            peg$silentFails++;
            s0 = peg$currPos;
            if (input.charCodeAt(peg$currPos) === 48) {
                s1 = peg$c85;
                peg$currPos++;
            }
            else {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c86);
                }
            }
            if (s1 !== peg$FAILED) {
                peg$savedPos = s0;
                s1 = peg$c87();
            }
            s0 = s1;
            if (s0 === peg$FAILED) {
                s0 = peg$currPos;
                s1 = peg$currPos;
                if (peg$c88.test(input.charAt(peg$currPos))) {
                    s2 = input.charAt(peg$currPos);
                    peg$currPos++;
                }
                else {
                    s2 = peg$FAILED;
                    if (peg$silentFails === 0) {
                        peg$fail(peg$c89);
                    }
                }
                if (s2 !== peg$FAILED) {
                    s3 = [];
                    if (peg$c90.test(input.charAt(peg$currPos))) {
                        s4 = input.charAt(peg$currPos);
                        peg$currPos++;
                    }
                    else {
                        s4 = peg$FAILED;
                        if (peg$silentFails === 0) {
                            peg$fail(peg$c91);
                        }
                    }
                    while (s4 !== peg$FAILED) {
                        s3.push(s4);
                        if (peg$c90.test(input.charAt(peg$currPos))) {
                            s4 = input.charAt(peg$currPos);
                            peg$currPos++;
                        }
                        else {
                            s4 = peg$FAILED;
                            if (peg$silentFails === 0) {
                                peg$fail(peg$c91);
                            }
                        }
                    }
                    if (s3 !== peg$FAILED) {
                        s2 = [s2, s3];
                        s1 = s2;
                    }
                    else {
                        peg$currPos = s1;
                        s1 = peg$FAILED;
                    }
                }
                else {
                    peg$currPos = s1;
                    s1 = peg$FAILED;
                }
                if (s1 !== peg$FAILED) {
                    peg$savedPos = s0;
                    s1 = peg$c92(s1);
                }
                s0 = s1;
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c84);
                }
            }
            return s0;
        }
        function peg$parseargName() {
            var s0, s1, s2, s3, s4;
            peg$silentFails++;
            s0 = peg$currPos;
            s1 = [];
            s2 = peg$currPos;
            s3 = peg$currPos;
            peg$silentFails++;
            s4 = peg$parsewhiteSpace();
            if (s4 === peg$FAILED) {
                s4 = peg$parsepatternSyntax();
            }
            peg$silentFails--;
            if (s4 === peg$FAILED) {
                s3 = undefined;
            }
            else {
                peg$currPos = s3;
                s3 = peg$FAILED;
            }
            if (s3 !== peg$FAILED) {
                if (input.length > peg$currPos) {
                    s4 = input.charAt(peg$currPos);
                    peg$currPos++;
                }
                else {
                    s4 = peg$FAILED;
                    if (peg$silentFails === 0) {
                        peg$fail(peg$c14);
                    }
                }
                if (s4 !== peg$FAILED) {
                    s3 = [s3, s4];
                    s2 = s3;
                }
                else {
                    peg$currPos = s2;
                    s2 = peg$FAILED;
                }
            }
            else {
                peg$currPos = s2;
                s2 = peg$FAILED;
            }
            if (s2 !== peg$FAILED) {
                while (s2 !== peg$FAILED) {
                    s1.push(s2);
                    s2 = peg$currPos;
                    s3 = peg$currPos;
                    peg$silentFails++;
                    s4 = peg$parsewhiteSpace();
                    if (s4 === peg$FAILED) {
                        s4 = peg$parsepatternSyntax();
                    }
                    peg$silentFails--;
                    if (s4 === peg$FAILED) {
                        s3 = undefined;
                    }
                    else {
                        peg$currPos = s3;
                        s3 = peg$FAILED;
                    }
                    if (s3 !== peg$FAILED) {
                        if (input.length > peg$currPos) {
                            s4 = input.charAt(peg$currPos);
                            peg$currPos++;
                        }
                        else {
                            s4 = peg$FAILED;
                            if (peg$silentFails === 0) {
                                peg$fail(peg$c14);
                            }
                        }
                        if (s4 !== peg$FAILED) {
                            s3 = [s3, s4];
                            s2 = s3;
                        }
                        else {
                            peg$currPos = s2;
                            s2 = peg$FAILED;
                        }
                    }
                    else {
                        peg$currPos = s2;
                        s2 = peg$FAILED;
                    }
                }
            }
            else {
                s1 = peg$FAILED;
            }
            if (s1 !== peg$FAILED) {
                s0 = input.substring(s0, peg$currPos);
            }
            else {
                s0 = s1;
            }
            peg$silentFails--;
            if (s0 === peg$FAILED) {
                s1 = peg$FAILED;
                if (peg$silentFails === 0) {
                    peg$fail(peg$c93);
                }
            }
            return s0;
        }
        var messageCtx = ['root'];
        function isNestedMessageText() {
            return messageCtx.length > 1;
        }
        function isInPluralOption() {
            return messageCtx[messageCtx.length - 1] === 'plural';
        }
        function insertLocation() {
            return options && options.captureLocation ? {
                location: location()
            } : {};
        }
        peg$result = peg$startRuleFunction();
        if (peg$result !== peg$FAILED && peg$currPos === input.length) {
            return peg$result;
        }
        else {
            if (peg$result !== peg$FAILED && peg$currPos < input.length) {
                peg$fail(peg$endExpectation());
            }
            throw peg$buildStructuredError(peg$maxFailExpected, peg$maxFailPos < input.length ? input.charAt(peg$maxFailPos) : null, peg$maxFailPos < input.length
                ? peg$computeLocation(peg$maxFailPos, peg$maxFailPos + 1)
                : peg$computeLocation(peg$maxFailPos, peg$maxFailPos));
        }
    }
    var pegParse = peg$parse;

    var __spreadArrays = (undefined && undefined.__spreadArrays) || function () {
        for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
        for (var r = Array(s), k = 0, i = 0; i < il; i++)
            for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
                r[k] = a[j];
        return r;
    };
    var PLURAL_HASHTAG_REGEX = /(^|[^\\])#/g;
    /**
     * Whether to convert `#` in plural rule options
     * to `{var, number}`
     * @param el AST Element
     * @param pluralStack current plural stack
     */
    function normalizeHashtagInPlural(els) {
        els.forEach(function (el) {
            // If we're encountering a plural el
            if (!isPluralElement(el) && !isSelectElement(el)) {
                return;
            }
            // Go down the options and search for # in any literal element
            Object.keys(el.options).forEach(function (id) {
                var _a;
                var opt = el.options[id];
                // If we got a match, we have to split this
                // and inject a NumberElement in the middle
                var matchingLiteralElIndex = -1;
                var literalEl = undefined;
                for (var i = 0; i < opt.value.length; i++) {
                    var el_1 = opt.value[i];
                    if (isLiteralElement(el_1) && PLURAL_HASHTAG_REGEX.test(el_1.value)) {
                        matchingLiteralElIndex = i;
                        literalEl = el_1;
                        break;
                    }
                }
                if (literalEl) {
                    var newValue = literalEl.value.replace(PLURAL_HASHTAG_REGEX, "$1{" + el.value + ", number}");
                    var newEls = pegParse(newValue);
                    (_a = opt.value).splice.apply(_a, __spreadArrays([matchingLiteralElIndex, 1], newEls));
                }
                normalizeHashtagInPlural(opt.value);
            });
        });
    }

    var __assign$1 = (undefined && undefined.__assign) || function () {
        __assign$1 = Object.assign || function(t) {
            for (var s, i = 1, n = arguments.length; i < n; i++) {
                s = arguments[i];
                for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                    t[p] = s[p];
            }
            return t;
        };
        return __assign$1.apply(this, arguments);
    };
    /**
     * https://unicode.org/reports/tr35/tr35-dates.html#Date_Field_Symbol_Table
     * Credit: https://github.com/caridy/intl-datetimeformat-pattern/blob/master/index.js
     * with some tweaks
     */
    var DATE_TIME_REGEX = /(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;
    /**
     * Parse Date time skeleton into Intl.DateTimeFormatOptions
     * Ref: https://unicode.org/reports/tr35/tr35-dates.html#Date_Field_Symbol_Table
     * @public
     * @param skeleton skeleton string
     */
    function parseDateTimeSkeleton(skeleton) {
        var result = {};
        skeleton.replace(DATE_TIME_REGEX, function (match) {
            var len = match.length;
            switch (match[0]) {
                // Era
                case 'G':
                    result.era = len === 4 ? 'long' : len === 5 ? 'narrow' : 'short';
                    break;
                // Year
                case 'y':
                    result.year = len === 2 ? '2-digit' : 'numeric';
                    break;
                case 'Y':
                case 'u':
                case 'U':
                case 'r':
                    throw new RangeError('`Y/u/U/r` (year) patterns are not supported, use `y` instead');
                // Quarter
                case 'q':
                case 'Q':
                    throw new RangeError('`q/Q` (quarter) patterns are not supported');
                // Month
                case 'M':
                case 'L':
                    result.month = ['numeric', '2-digit', 'short', 'long', 'narrow'][len - 1];
                    break;
                // Week
                case 'w':
                case 'W':
                    throw new RangeError('`w/W` (week) patterns are not supported');
                case 'd':
                    result.day = ['numeric', '2-digit'][len - 1];
                    break;
                case 'D':
                case 'F':
                case 'g':
                    throw new RangeError('`D/F/g` (day) patterns are not supported, use `d` instead');
                // Weekday
                case 'E':
                    result.weekday = len === 4 ? 'short' : len === 5 ? 'narrow' : 'short';
                    break;
                case 'e':
                    if (len < 4) {
                        throw new RangeError('`e..eee` (weekday) patterns are not supported');
                    }
                    result.weekday = ['short', 'long', 'narrow', 'short'][len - 4];
                    break;
                case 'c':
                    if (len < 4) {
                        throw new RangeError('`c..ccc` (weekday) patterns are not supported');
                    }
                    result.weekday = ['short', 'long', 'narrow', 'short'][len - 4];
                    break;
                // Period
                case 'a': // AM, PM
                    result.hour12 = true;
                    break;
                case 'b': // am, pm, noon, midnight
                case 'B': // flexible day periods
                    throw new RangeError('`b/B` (period) patterns are not supported, use `a` instead');
                // Hour
                case 'h':
                    result.hourCycle = 'h12';
                    result.hour = ['numeric', '2-digit'][len - 1];
                    break;
                case 'H':
                    result.hourCycle = 'h23';
                    result.hour = ['numeric', '2-digit'][len - 1];
                    break;
                case 'K':
                    result.hourCycle = 'h11';
                    result.hour = ['numeric', '2-digit'][len - 1];
                    break;
                case 'k':
                    result.hourCycle = 'h24';
                    result.hour = ['numeric', '2-digit'][len - 1];
                    break;
                case 'j':
                case 'J':
                case 'C':
                    throw new RangeError('`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead');
                // Minute
                case 'm':
                    result.minute = ['numeric', '2-digit'][len - 1];
                    break;
                // Second
                case 's':
                    result.second = ['numeric', '2-digit'][len - 1];
                    break;
                case 'S':
                case 'A':
                    throw new RangeError('`S/A` (second) pattenrs are not supported, use `s` instead');
                // Zone
                case 'z': // 1..3, 4: specific non-location format
                    result.timeZoneName = len < 4 ? 'short' : 'long';
                    break;
                case 'Z': // 1..3, 4, 5: The ISO8601 varios formats
                case 'O': // 1, 4: miliseconds in day short, long
                case 'v': // 1, 4: generic non-location format
                case 'V': // 1, 2, 3, 4: time zone ID or city
                case 'X': // 1, 2, 3, 4: The ISO8601 varios formats
                case 'x': // 1, 2, 3, 4: The ISO8601 varios formats
                    throw new RangeError('`Z/O/v/V/X/x` (timeZone) pattenrs are not supported, use `z` instead');
            }
            return '';
        });
        return result;
    }
    function icuUnitToEcma(unit) {
        return unit.replace(/^(.*?)-/, '');
    }
    var FRACTION_PRECISION_REGEX = /^\.(?:(0+)(\+|#+)?)?$/g;
    var SIGNIFICANT_PRECISION_REGEX = /^(@+)?(\+|#+)?$/g;
    function parseSignificantPrecision(str) {
        var result = {};
        str.replace(SIGNIFICANT_PRECISION_REGEX, function (_, g1, g2) {
            // @@@ case
            if (typeof g2 !== 'string') {
                result.minimumSignificantDigits = g1.length;
                result.maximumSignificantDigits = g1.length;
            }
            // @@@+ case
            else if (g2 === '+') {
                result.minimumSignificantDigits = g1.length;
            }
            // .### case
            else if (g1[0] === '#') {
                result.maximumSignificantDigits = g1.length;
            }
            // .@@## or .@@@ case
            else {
                result.minimumSignificantDigits = g1.length;
                result.maximumSignificantDigits =
                    g1.length + (typeof g2 === 'string' ? g2.length : 0);
            }
            return '';
        });
        return result;
    }
    function parseSign(str) {
        switch (str) {
            case 'sign-auto':
                return {
                    signDisplay: 'auto',
                };
            case 'sign-accounting':
                return {
                    currencySign: 'accounting',
                };
            case 'sign-always':
                return {
                    signDisplay: 'always',
                };
            case 'sign-accounting-always':
                return {
                    signDisplay: 'always',
                    currencySign: 'accounting',
                };
            case 'sign-except-zero':
                return {
                    signDisplay: 'exceptZero',
                };
            case 'sign-accounting-except-zero':
                return {
                    signDisplay: 'exceptZero',
                    currencySign: 'accounting',
                };
            case 'sign-never':
                return {
                    signDisplay: 'never',
                };
        }
    }
    function parseNotationOptions(opt) {
        var result = {};
        var signOpts = parseSign(opt);
        if (signOpts) {
            return signOpts;
        }
        return result;
    }
    /**
     * https://github.com/unicode-org/icu/blob/master/docs/userguide/format_parse/numbers/skeletons.md#skeleton-stems-and-options
     */
    function convertNumberSkeletonToNumberFormatOptions(tokens) {
        var result = {};
        for (var _i = 0, tokens_1 = tokens; _i < tokens_1.length; _i++) {
            var token = tokens_1[_i];
            switch (token.stem) {
                case 'percent':
                    result.style = 'percent';
                    continue;
                case 'currency':
                    result.style = 'currency';
                    result.currency = token.options[0];
                    continue;
                case 'group-off':
                    result.useGrouping = false;
                    continue;
                case 'precision-integer':
                    result.maximumFractionDigits = 0;
                    continue;
                case 'measure-unit':
                    result.style = 'unit';
                    result.unit = icuUnitToEcma(token.options[0]);
                    continue;
                case 'compact-short':
                    result.notation = 'compact';
                    result.compactDisplay = 'short';
                    continue;
                case 'compact-long':
                    result.notation = 'compact';
                    result.compactDisplay = 'long';
                    continue;
                case 'scientific':
                    result = __assign$1(__assign$1(__assign$1({}, result), { notation: 'scientific' }), token.options.reduce(function (all, opt) { return (__assign$1(__assign$1({}, all), parseNotationOptions(opt))); }, {}));
                    continue;
                case 'engineering':
                    result = __assign$1(__assign$1(__assign$1({}, result), { notation: 'engineering' }), token.options.reduce(function (all, opt) { return (__assign$1(__assign$1({}, all), parseNotationOptions(opt))); }, {}));
                    continue;
                case 'notation-simple':
                    result.notation = 'standard';
                    continue;
                // https://github.com/unicode-org/icu/blob/master/icu4c/source/i18n/unicode/unumberformatter.h
                case 'unit-width-narrow':
                    result.currencyDisplay = 'narrowSymbol';
                    result.unitDisplay = 'narrow';
                    continue;
                case 'unit-width-short':
                    result.currencyDisplay = 'code';
                    result.unitDisplay = 'short';
                    continue;
                case 'unit-width-full-name':
                    result.currencyDisplay = 'name';
                    result.unitDisplay = 'long';
                    continue;
                case 'unit-width-iso-code':
                    result.currencyDisplay = 'symbol';
                    continue;
            }
            // Precision
            // https://github.com/unicode-org/icu/blob/master/docs/userguide/format_parse/numbers/skeletons.md#fraction-precision
            if (FRACTION_PRECISION_REGEX.test(token.stem)) {
                if (token.options.length > 1) {
                    throw new RangeError('Fraction-precision stems only accept a single optional option');
                }
                token.stem.replace(FRACTION_PRECISION_REGEX, function (match, g1, g2) {
                    // precision-integer case
                    if (match === '.') {
                        result.maximumFractionDigits = 0;
                    }
                    // .000+ case
                    else if (g2 === '+') {
                        result.minimumFractionDigits = g2.length;
                    }
                    // .### case
                    else if (g1[0] === '#') {
                        result.maximumFractionDigits = g1.length;
                    }
                    // .00## or .000 case
                    else {
                        result.minimumFractionDigits = g1.length;
                        result.maximumFractionDigits =
                            g1.length + (typeof g2 === 'string' ? g2.length : 0);
                    }
                    return '';
                });
                if (token.options.length) {
                    result = __assign$1(__assign$1({}, result), parseSignificantPrecision(token.options[0]));
                }
                continue;
            }
            if (SIGNIFICANT_PRECISION_REGEX.test(token.stem)) {
                result = __assign$1(__assign$1({}, result), parseSignificantPrecision(token.stem));
                continue;
            }
            var signOpts = parseSign(token.stem);
            if (signOpts) {
                result = __assign$1(__assign$1({}, result), signOpts);
            }
        }
        return result;
    }

    function parse(input, opts) {
        var els = pegParse(input, opts);
        if (!opts || opts.normalizeHashtagInPlural !== false) {
            normalizeHashtagInPlural(els);
        }
        return els;
    }

    /*
    Copyright (c) 2014, Yahoo! Inc. All rights reserved.
    Copyrights licensed under the New BSD License.
    See the accompanying LICENSE file for terms.
    */
    var __spreadArrays$1 = (undefined && undefined.__spreadArrays) || function () {
        for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
        for (var r = Array(s), k = 0, i = 0; i < il; i++)
            for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
                r[k] = a[j];
        return r;
    };
    // -- Utilities ----------------------------------------------------------------
    function getCacheId(inputs) {
        return JSON.stringify(inputs.map(function (input) {
            return input && typeof input === 'object' ? orderedProps(input) : input;
        }));
    }
    function orderedProps(obj) {
        return Object.keys(obj)
            .sort()
            .map(function (k) {
            var _a;
            return (_a = {}, _a[k] = obj[k], _a);
        });
    }
    var memoizeFormatConstructor = function (FormatConstructor, cache) {
        if (cache === void 0) { cache = {}; }
        return function () {
            var _a;
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            var cacheId = getCacheId(args);
            var format = cacheId && cache[cacheId];
            if (!format) {
                format = new ((_a = FormatConstructor).bind.apply(_a, __spreadArrays$1([void 0], args)))();
                if (cacheId) {
                    cache[cacheId] = format;
                }
            }
            return format;
        };
    };

    var __extends$1 = (undefined && undefined.__extends) || (function () {
        var extendStatics = function (d, b) {
            extendStatics = Object.setPrototypeOf ||
                ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
                function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
            return extendStatics(d, b);
        };
        return function (d, b) {
            extendStatics(d, b);
            function __() { this.constructor = d; }
            d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
        };
    })();
    var __spreadArrays$2 = (undefined && undefined.__spreadArrays) || function () {
        for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
        for (var r = Array(s), k = 0, i = 0; i < il; i++)
            for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
                r[k] = a[j];
        return r;
    };
    var FormatError = /** @class */ (function (_super) {
        __extends$1(FormatError, _super);
        function FormatError(msg, variableId) {
            var _this = _super.call(this, msg) || this;
            _this.variableId = variableId;
            return _this;
        }
        return FormatError;
    }(Error));
    function mergeLiteral(parts) {
        if (parts.length < 2) {
            return parts;
        }
        return parts.reduce(function (all, part) {
            var lastPart = all[all.length - 1];
            if (!lastPart ||
                lastPart.type !== 0 /* literal */ ||
                part.type !== 0 /* literal */) {
                all.push(part);
            }
            else {
                lastPart.value += part.value;
            }
            return all;
        }, []);
    }
    // TODO(skeleton): add skeleton support
    function formatToParts(els, locales, formatters, formats, values, currentPluralValue, 
    // For debugging
    originalMessage) {
        // Hot path for straight simple msg translations
        if (els.length === 1 && isLiteralElement(els[0])) {
            return [
                {
                    type: 0 /* literal */,
                    value: els[0].value,
                },
            ];
        }
        var result = [];
        for (var _i = 0, els_1 = els; _i < els_1.length; _i++) {
            var el = els_1[_i];
            // Exit early for string parts.
            if (isLiteralElement(el)) {
                result.push({
                    type: 0 /* literal */,
                    value: el.value,
                });
                continue;
            }
            // TODO: should this part be literal type?
            // Replace `#` in plural rules with the actual numeric value.
            if (isPoundElement(el)) {
                if (typeof currentPluralValue === 'number') {
                    result.push({
                        type: 0 /* literal */,
                        value: formatters.getNumberFormat(locales).format(currentPluralValue),
                    });
                }
                continue;
            }
            var varName = el.value;
            // Enforce that all required values are provided by the caller.
            if (!(values && varName in values)) {
                throw new FormatError("The intl string context variable \"" + varName + "\" was not provided to the string \"" + originalMessage + "\"");
            }
            var value = values[varName];
            if (isArgumentElement(el)) {
                if (!value || typeof value === 'string' || typeof value === 'number') {
                    value =
                        typeof value === 'string' || typeof value === 'number'
                            ? String(value)
                            : '';
                }
                result.push({
                    type: 1 /* argument */,
                    value: value,
                });
                continue;
            }
            // Recursively format plural and select parts' option — which can be a
            // nested pattern structure. The choosing of the option to use is
            // abstracted-by and delegated-to the part helper object.
            if (isDateElement(el)) {
                var style = typeof el.style === 'string' ? formats.date[el.style] : undefined;
                result.push({
                    type: 0 /* literal */,
                    value: formatters
                        .getDateTimeFormat(locales, style)
                        .format(value),
                });
                continue;
            }
            if (isTimeElement(el)) {
                var style = typeof el.style === 'string'
                    ? formats.time[el.style]
                    : isDateTimeSkeleton(el.style)
                        ? parseDateTimeSkeleton(el.style.pattern)
                        : undefined;
                result.push({
                    type: 0 /* literal */,
                    value: formatters
                        .getDateTimeFormat(locales, style)
                        .format(value),
                });
                continue;
            }
            if (isNumberElement(el)) {
                var style = typeof el.style === 'string'
                    ? formats.number[el.style]
                    : isNumberSkeleton(el.style)
                        ? convertNumberSkeletonToNumberFormatOptions(el.style.tokens)
                        : undefined;
                result.push({
                    type: 0 /* literal */,
                    value: formatters
                        .getNumberFormat(locales, style)
                        .format(value),
                });
                continue;
            }
            if (isSelectElement(el)) {
                var opt = el.options[value] || el.options.other;
                if (!opt) {
                    throw new RangeError("Invalid values for \"" + el.value + "\": \"" + value + "\". Options are \"" + Object.keys(el.options).join('", "') + "\"");
                }
                result.push.apply(result, formatToParts(opt.value, locales, formatters, formats, values));
                continue;
            }
            if (isPluralElement(el)) {
                var opt = el.options["=" + value];
                if (!opt) {
                    if (!Intl.PluralRules) {
                        throw new FormatError("Intl.PluralRules is not available in this environment.\nTry polyfilling it using \"@formatjs/intl-pluralrules\"\n");
                    }
                    var rule = formatters
                        .getPluralRules(locales, { type: el.pluralType })
                        .select(value - (el.offset || 0));
                    opt = el.options[rule] || el.options.other;
                }
                if (!opt) {
                    throw new RangeError("Invalid values for \"" + el.value + "\": \"" + value + "\". Options are \"" + Object.keys(el.options).join('", "') + "\"");
                }
                result.push.apply(result, formatToParts(opt.value, locales, formatters, formats, values, value - (el.offset || 0)));
                continue;
            }
        }
        return mergeLiteral(result);
    }
    function formatToString(els, locales, formatters, formats, values, 
    // For debugging
    originalMessage) {
        var parts = formatToParts(els, locales, formatters, formats, values, undefined, originalMessage);
        // Hot path for straight simple msg translations
        if (parts.length === 1) {
            return parts[0].value;
        }
        return parts.reduce(function (all, part) { return (all += part.value); }, '');
    }
    // Singleton
    var domParser;
    var TOKEN_DELIMITER = '@@';
    var TOKEN_REGEX = /@@(\d+_\d+)@@/g;
    var counter = 0;
    function generateId() {
        return Date.now() + "_" + ++counter;
    }
    function restoreRichPlaceholderMessage(text, objectParts) {
        return text
            .split(TOKEN_REGEX)
            .filter(Boolean)
            .map(function (c) { return (objectParts[c] != null ? objectParts[c] : c); })
            .reduce(function (all, c) {
            if (!all.length) {
                all.push(c);
            }
            else if (typeof c === 'string' &&
                typeof all[all.length - 1] === 'string') {
                all[all.length - 1] += c;
            }
            else {
                all.push(c);
            }
            return all;
        }, []);
    }
    /**
     * Not exhaustive, just for sanity check
     */
    var SIMPLE_XML_REGEX = /(<([0-9a-zA-Z-_]*?)>(.*?)<\/([0-9a-zA-Z-_]*?)>)|(<[0-9a-zA-Z-_]*?\/>)/;
    var TEMPLATE_ID = Date.now() + '@@';
    var VOID_ELEMENTS = [
        'area',
        'base',
        'br',
        'col',
        'embed',
        'hr',
        'img',
        'input',
        'link',
        'meta',
        'param',
        'source',
        'track',
        'wbr',
    ];
    function formatHTMLElement(el, objectParts, values) {
        var tagName = el.tagName;
        var outerHTML = el.outerHTML, textContent = el.textContent, childNodes = el.childNodes;
        // Regular text
        if (!tagName) {
            return restoreRichPlaceholderMessage(textContent || '', objectParts);
        }
        tagName = tagName.toLowerCase();
        var isVoidElement = ~VOID_ELEMENTS.indexOf(tagName);
        var formatFnOrValue = values[tagName];
        if (formatFnOrValue && isVoidElement) {
            throw new FormatError(tagName + " is a self-closing tag and can not be used, please use another tag name.");
        }
        if (!childNodes.length) {
            return [outerHTML];
        }
        var chunks = Array.prototype.slice.call(childNodes).reduce(function (all, child) {
            return all.concat(formatHTMLElement(child, objectParts, values));
        }, []);
        // Legacy HTML
        if (!formatFnOrValue) {
            return __spreadArrays$2(["<" + tagName + ">"], chunks, ["</" + tagName + ">"]);
        }
        // HTML Tag replacement
        if (typeof formatFnOrValue === 'function') {
            return [formatFnOrValue.apply(void 0, chunks)];
        }
        return [formatFnOrValue];
    }
    function formatHTMLMessage(els, locales, formatters, formats, values, 
    // For debugging
    originalMessage) {
        var parts = formatToParts(els, locales, formatters, formats, values, undefined, originalMessage);
        var objectParts = {};
        var formattedMessage = parts.reduce(function (all, part) {
            if (part.type === 0 /* literal */) {
                return (all += part.value);
            }
            var id = generateId();
            objectParts[id] = part.value;
            return (all += "" + TOKEN_DELIMITER + id + TOKEN_DELIMITER);
        }, '');
        // Not designed to filter out aggressively
        if (!SIMPLE_XML_REGEX.test(formattedMessage)) {
            return restoreRichPlaceholderMessage(formattedMessage, objectParts);
        }
        if (!values) {
            throw new FormatError('Message has placeholders but no values was given');
        }
        if (typeof DOMParser === 'undefined') {
            throw new FormatError('Cannot format XML message without DOMParser');
        }
        if (!domParser) {
            domParser = new DOMParser();
        }
        var content = domParser
            .parseFromString("<formatted-message id=\"" + TEMPLATE_ID + "\">" + formattedMessage + "</formatted-message>", 'text/html')
            .getElementById(TEMPLATE_ID);
        if (!content) {
            throw new FormatError("Malformed HTML message " + formattedMessage);
        }
        var tagsToFormat = Object.keys(values).filter(function (varName) { return !!content.getElementsByTagName(varName).length; });
        // No tags to format
        if (!tagsToFormat.length) {
            return restoreRichPlaceholderMessage(formattedMessage, objectParts);
        }
        var caseSensitiveTags = tagsToFormat.filter(function (tagName) { return tagName !== tagName.toLowerCase(); });
        if (caseSensitiveTags.length) {
            throw new FormatError("HTML tag must be lowercased but the following tags are not: " + caseSensitiveTags.join(', '));
        }
        // We're doing this since top node is `<formatted-message/>` which does not have a formatter
        return Array.prototype.slice
            .call(content.childNodes)
            .reduce(function (all, child) { return all.concat(formatHTMLElement(child, objectParts, values)); }, []);
    }

    /*
    Copyright (c) 2014, Yahoo! Inc. All rights reserved.
    Copyrights licensed under the New BSD License.
    See the accompanying LICENSE file for terms.
    */
    var __assign$2 = (undefined && undefined.__assign) || function () {
        __assign$2 = Object.assign || function(t) {
            for (var s, i = 1, n = arguments.length; i < n; i++) {
                s = arguments[i];
                for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                    t[p] = s[p];
            }
            return t;
        };
        return __assign$2.apply(this, arguments);
    };
    // -- MessageFormat --------------------------------------------------------
    function mergeConfig(c1, c2) {
        if (!c2) {
            return c1;
        }
        return __assign$2(__assign$2(__assign$2({}, (c1 || {})), (c2 || {})), Object.keys(c1).reduce(function (all, k) {
            all[k] = __assign$2(__assign$2({}, c1[k]), (c2[k] || {}));
            return all;
        }, {}));
    }
    function mergeConfigs(defaultConfig, configs) {
        if (!configs) {
            return defaultConfig;
        }
        return Object.keys(defaultConfig).reduce(function (all, k) {
            all[k] = mergeConfig(defaultConfig[k], configs[k]);
            return all;
        }, __assign$2({}, defaultConfig));
    }
    function createDefaultFormatters(cache) {
        if (cache === void 0) { cache = {
            number: {},
            dateTime: {},
            pluralRules: {},
        }; }
        return {
            getNumberFormat: memoizeFormatConstructor(Intl.NumberFormat, cache.number),
            getDateTimeFormat: memoizeFormatConstructor(Intl.DateTimeFormat, cache.dateTime),
            getPluralRules: memoizeFormatConstructor(Intl.PluralRules, cache.pluralRules),
        };
    }
    var IntlMessageFormat = /** @class */ (function () {
        function IntlMessageFormat(message, locales, overrideFormats, opts) {
            var _this = this;
            if (locales === void 0) { locales = IntlMessageFormat.defaultLocale; }
            this.formatterCache = {
                number: {},
                dateTime: {},
                pluralRules: {},
            };
            this.format = function (values) {
                return formatToString(_this.ast, _this.locales, _this.formatters, _this.formats, values, _this.message);
            };
            this.formatToParts = function (values) {
                return formatToParts(_this.ast, _this.locales, _this.formatters, _this.formats, values, undefined, _this.message);
            };
            this.formatHTMLMessage = function (values) {
                return formatHTMLMessage(_this.ast, _this.locales, _this.formatters, _this.formats, values, _this.message);
            };
            this.resolvedOptions = function () { return ({
                locale: Intl.NumberFormat.supportedLocalesOf(_this.locales)[0],
            }); };
            this.getAst = function () { return _this.ast; };
            if (typeof message === 'string') {
                this.message = message;
                if (!IntlMessageFormat.__parse) {
                    throw new TypeError('IntlMessageFormat.__parse must be set to process `message` of type `string`');
                }
                // Parse string messages into an AST.
                this.ast = IntlMessageFormat.__parse(message, {
                    normalizeHashtagInPlural: false,
                });
            }
            else {
                this.ast = message;
            }
            if (!Array.isArray(this.ast)) {
                throw new TypeError('A message must be provided as a String or AST.');
            }
            // Creates a new object with the specified `formats` merged with the default
            // formats.
            this.formats = mergeConfigs(IntlMessageFormat.formats, overrideFormats);
            // Defined first because it's used to build the format pattern.
            this.locales = locales;
            this.formatters =
                (opts && opts.formatters) || createDefaultFormatters(this.formatterCache);
        }
        IntlMessageFormat.defaultLocale = new Intl.NumberFormat().resolvedOptions().locale;
        IntlMessageFormat.__parse = parse;
        // Default format options used as the prototype of the `formats` provided to the
        // constructor. These are used when constructing the internal Intl.NumberFormat
        // and Intl.DateTimeFormat instances.
        IntlMessageFormat.formats = {
            number: {
                currency: {
                    style: 'currency',
                },
                percent: {
                    style: 'percent',
                },
            },
            date: {
                short: {
                    month: 'numeric',
                    day: 'numeric',
                    year: '2-digit',
                },
                medium: {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                },
                long: {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric',
                },
                full: {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric',
                },
            },
            time: {
                short: {
                    hour: 'numeric',
                    minute: 'numeric',
                },
                medium: {
                    hour: 'numeric',
                    minute: 'numeric',
                    second: 'numeric',
                },
                long: {
                    hour: 'numeric',
                    minute: 'numeric',
                    second: 'numeric',
                    timeZoneName: 'short',
                },
                full: {
                    hour: 'numeric',
                    minute: 'numeric',
                    second: 'numeric',
                    timeZoneName: 'short',
                },
            },
        };
        return IntlMessageFormat;
    }());

    const o=(n,e="")=>{const t={};for(const r in n){const i=e+r;"object"==typeof n[r]?Object.assign(t,o(n[r],i+".")):t[i]=n[r];}return t};let r;const i=writable({});function a(n){return n in r}function l(n,e){if(a(n)){const t=function(n){return r[n]||null}(n);if(e in t)return t[e]}return null}function s(n){return null==n||a(n)?n:s(D(n))}function c(n,...e){const t=e.map(n=>o(n));i.update(e=>(e[n]=Object.assign(e[n]||{},...t),e));}const u=derived([i],([n])=>Object.keys(n));i.subscribe(n=>r=n);const m={};function f(n){return m[n]}function d(n){return I(n).reverse().some(n=>{var e;return null===(e=f(n))||void 0===e?void 0:e.size})}function w(n,e){return Promise.all(e.map(e=>(function(n,e){m[n].delete(e),0===m[n].size&&delete m[n];}(n,e),e().then(n=>n.default||n)))).then(e=>c(n,...e))}const g={};function b(n){if(!d(n))return n in g?g[n]:void 0;const e=function(n){return I(n).reverse().map(n=>{const e=f(n);return [n,e?[...e]:[]]}).filter(([,n])=>n.length>0)}(n);return g[n]=Promise.all(e.map(([n,e])=>w(n,e))).then(()=>{if(d(n))return b(n);delete g[n];}),g[n]}/*! *****************************************************************************
    Copyright (c) Microsoft Corporation.

    Permission to use, copy, modify, and/or distribute this software for any
    purpose with or without fee is hereby granted.

    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
    REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
    AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
    INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
    LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
    OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
    PERFORMANCE OF THIS SOFTWARE.
    ***************************************************************************** */function h(n,e){var t={};for(var o in n)Object.prototype.hasOwnProperty.call(n,o)&&e.indexOf(o)<0&&(t[o]=n[o]);if(null!=n&&"function"==typeof Object.getOwnPropertySymbols){var r=0;for(o=Object.getOwnPropertySymbols(n);r<o.length;r++)e.indexOf(o[r])<0&&Object.prototype.propertyIsEnumerable.call(n,o[r])&&(t[o[r]]=n[o[r]]);}return t}const y={fallbackLocale:null,initialLocale:null,loadingDelay:200,formats:{number:{scientific:{notation:"scientific"},engineering:{notation:"engineering"},compactLong:{notation:"compact",compactDisplay:"long"},compactShort:{notation:"compact",compactDisplay:"short"}},date:{short:{month:"numeric",day:"numeric",year:"2-digit"},medium:{month:"short",day:"numeric",year:"numeric"},long:{month:"long",day:"numeric",year:"numeric"},full:{weekday:"long",month:"long",day:"numeric",year:"numeric"}},time:{short:{hour:"numeric",minute:"numeric"},medium:{hour:"numeric",minute:"numeric",second:"numeric"},long:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"},full:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"}}},warnOnMissingMessages:!0};function O(){return y}function v(n){const{formats:e}=n,t=h(n,["formats"]),o=n.initialLocale||n.fallbackLocale;return Object.assign(y,t,{initialLocale:o}),e&&("number"in e&&Object.assign(y.formats.number,e.number),"date"in e&&Object.assign(y.formats.date,e.date),"time"in e&&Object.assign(y.formats.time,e.time)),k.set(o)}const j=writable(!1);let L;const k=writable(null);function x(n,e){return 0===e.indexOf(n)&&n!==e}function E(n,e){return n===e||x(n,e)||x(e,n)}function D(n){const e=n.lastIndexOf("-");if(e>0)return n.slice(0,e);const{fallbackLocale:t}=O();return t&&!E(n,t)?t:null}function I(n){const e=n.split("-").map((n,e,t)=>t.slice(0,e+1).join("-")),{fallbackLocale:t}=O();return t&&!E(n,t)?e.concat(I(t)):e}function N(){return L}k.subscribe(n=>{L=n,"undefined"!=typeof window&&document.documentElement.setAttribute("lang",n);});const P=k.set;k.set=n=>{if(s(n)&&d(n)){const{loadingDelay:e}=O();let t;return "undefined"!=typeof window&&null!=N()&&e?t=window.setTimeout(()=>j.set(!0),e):j.set(!0),b(n).then(()=>{P(n);}).finally(()=>{clearTimeout(t),j.set(!1);})}return P(n)},k.update=n=>P(n(L));const M=()=>"undefined"==typeof window?null:window.navigator.language||window.navigator.languages[0],Z={},C=(n,e)=>{if(null==e)return null;const t=l(e,n);return t||C(n,D(e))},J=(n,e)=>{if(e in Z&&n in Z[e])return Z[e][n];const t=C(n,e);return t?((n,e,t)=>t?(e in Z||(Z[e]={}),n in Z[e]||(Z[e][n]=t),t):t)(n,e,t):null},U=n=>{const e=Object.create(null);return t=>{const o=JSON.stringify(t);return o in e?e[o]:e[o]=n(t)}},_=(n,e)=>{const{formats:t}=O();if(n in t&&e in t[n])return t[n][e];throw new Error(`[svelte-i18n] Unknown "${e}" ${n} format.`)},q=U(n=>{var{locale:e,format:t}=n,o=h(n,["locale","format"]);if(null==e)throw new Error('[svelte-i18n] A "locale" must be set to format numbers');return t&&(o=_("number",t)),new Intl.NumberFormat(e,o)}),B=U(n=>{var{locale:e,format:t}=n,o=h(n,["locale","format"]);if(null==e)throw new Error('[svelte-i18n] A "locale" must be set to format dates');return t?o=_("date",t):0===Object.keys(o).length&&(o=_("date","short")),new Intl.DateTimeFormat(e,o)}),G=U(n=>{var{locale:e,format:t}=n,o=h(n,["locale","format"]);if(null==e)throw new Error('[svelte-i18n] A "locale" must be set to format time values');return t?o=_("time",t):0===Object.keys(o).length&&(o=_("time","short")),new Intl.DateTimeFormat(e,o)}),H=(n={})=>{var{locale:e=N()}=n,t=h(n,["locale"]);return q(Object.assign({locale:e},t))},K=(n={})=>{var{locale:e=N()}=n,t=h(n,["locale"]);return B(Object.assign({locale:e},t))},Q=(n={})=>{var{locale:e=N()}=n,t=h(n,["locale"]);return G(Object.assign({locale:e},t))},R=U((n,e=N())=>new IntlMessageFormat(n,e,O().formats)),V=(n,e={})=>{"object"==typeof n&&(n=(e=n).id);const{values:t,locale:o=N(),default:r}=e;if(null==o)throw new Error("[svelte-i18n] Cannot format a message without first setting the initial locale.");const i=J(n,o);return i?t?R(i,o).format(t):i:(O().warnOnMissingMessages&&console.warn(`[svelte-i18n] The message "${n}" was not found in "${I(o).join('", "')}".${d(N())?"\n\nNote: there are at least one loader still registered to this locale that wasn't executed.":""}`),r||n)},W=(n,e)=>Q(e).format(n),X=(n,e)=>K(e).format(n),Y=(n,e)=>H(e).format(n),nn=derived([k,i],()=>V),en=derived([k],()=>W),tn=derived([k],()=>X),on=derived([k],()=>Y);

    /* src/InfiniteScroll.svelte generated by Svelte v3.29.4 */
    const file = "src/InfiniteScroll.svelte";

    function create_fragment(ctx) {
    	let div;

    	const block = {
    		c: function create() {
    			div = element("div");
    			set_style(div, "width", "0px");
    			add_location(div, file, 48, 0, 1226);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			/*div_binding*/ ctx[4](div);
    		},
    		p: noop,
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			/*div_binding*/ ctx[4](null);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance($$self, $$props, $$invalidate) {
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots("InfiniteScroll", slots, []);
    	let { threshold = 0 } = $$props;
    	let { horizontal = false } = $$props;

    	//export let elementScroll;
    	let elementScroll;

    	let { hasMore = false } = $$props;
    	const dispatch = createEventDispatcher();
    	let isLoadMore = false;
    	let component;

    	const onScroll = e => {
    		const element = e.target;

    		const offset = horizontal
    		? e.target.scrollWidth - e.target.clientWidth - e.target.scrollLeft
    		: e.target.scrollHeight - e.target.clientHeight - e.target.scrollTop;

    		if (offset <= threshold) {
    			if (!isLoadMore && hasMore) {
    				dispatch("loadMore");
    			}

    			isLoadMore = true;
    		} else {
    			isLoadMore = false;
    		}
    	};

    	onDestroy(() => {
    		if (component || elementScroll) {
    			const element = elementScroll ? elementScroll : component.parentNode;
    			element.removeEventListener("scroll", null);
    			element.removeEventListener("resize", null);
    		}
    	});

    	const writable_props = ["threshold", "horizontal", "hasMore"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<InfiniteScroll> was created with unknown prop '${key}'`);
    	});

    	function div_binding($$value) {
    		binding_callbacks[$$value ? "unshift" : "push"](() => {
    			component = $$value;
    			$$invalidate(0, component);
    		});
    	}

    	$$self.$$set = $$props => {
    		if ("threshold" in $$props) $$invalidate(1, threshold = $$props.threshold);
    		if ("horizontal" in $$props) $$invalidate(2, horizontal = $$props.horizontal);
    		if ("hasMore" in $$props) $$invalidate(3, hasMore = $$props.hasMore);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		onDestroy,
    		createEventDispatcher,
    		threshold,
    		horizontal,
    		elementScroll,
    		hasMore,
    		dispatch,
    		isLoadMore,
    		component,
    		onScroll
    	});

    	$$self.$inject_state = $$props => {
    		if ("threshold" in $$props) $$invalidate(1, threshold = $$props.threshold);
    		if ("horizontal" in $$props) $$invalidate(2, horizontal = $$props.horizontal);
    		if ("elementScroll" in $$props) $$invalidate(6, elementScroll = $$props.elementScroll);
    		if ("hasMore" in $$props) $$invalidate(3, hasMore = $$props.hasMore);
    		if ("isLoadMore" in $$props) isLoadMore = $$props.isLoadMore;
    		if ("component" in $$props) $$invalidate(0, component = $$props.component);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*component*/ 1) {
    			 {
    				if (component || elementScroll) {
    					const element = elementScroll ? elementScroll : component.parentNode;
    					element.addEventListener("scroll", onScroll);
    					element.addEventListener("resize", onScroll);
    				}
    			}
    		}
    	};

    	return [component, threshold, horizontal, hasMore, div_binding];
    }

    class InfiniteScroll extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance, create_fragment, safe_not_equal, { threshold: 1, horizontal: 2, hasMore: 3 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "InfiniteScroll",
    			options,
    			id: create_fragment.name
    		});
    	}

    	get threshold() {
    		throw new Error("<InfiniteScroll>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set threshold(value) {
    		throw new Error("<InfiniteScroll>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get horizontal() {
    		throw new Error("<InfiniteScroll>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set horizontal(value) {
    		throw new Error("<InfiniteScroll>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get hasMore() {
    		throw new Error("<InfiniteScroll>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set hasMore(value) {
    		throw new Error("<InfiniteScroll>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    var commonjsGlobal = typeof globalThis !== 'undefined' ? globalThis : typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {};

    function unwrapExports (x) {
    	return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, 'default') ? x['default'] : x;
    }

    function createCommonjsModule(fn, basedir, module) {
    	return module = {
    	  path: basedir,
    	  exports: {},
    	  require: function (path, base) {
          return commonjsRequire(path, (base === undefined || base === null) ? module.path : base);
        }
    	}, fn(module, module.exports), module.exports;
    }

    function commonjsRequire () {
    	throw new Error('Dynamic requires are not currently supported by @rollup/plugin-commonjs');
    }

    var dayjs_min = createCommonjsModule(function (module, exports) {
    !function(t,e){module.exports=e();}(commonjsGlobal,function(){var t="millisecond",e="second",n="minute",r="hour",i="day",s="week",u="month",a="quarter",o="year",f="date",h=/^(\d{4})[-/]?(\d{1,2})?[-/]?(\d{0,2})[^0-9]*(\d{1,2})?:?(\d{1,2})?:?(\d{1,2})?.?(\d+)?$/,c=/\[([^\]]+)]|Y{2,4}|M{1,4}|D{1,2}|d{1,4}|H{1,2}|h{1,2}|a|A|m{1,2}|s{1,2}|Z{1,2}|SSS/g,d={name:"en",weekdays:"Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday".split("_"),months:"January_February_March_April_May_June_July_August_September_October_November_December".split("_")},$=function(t,e,n){var r=String(t);return !r||r.length>=e?t:""+Array(e+1-r.length).join(n)+t},l={s:$,z:function(t){var e=-t.utcOffset(),n=Math.abs(e),r=Math.floor(n/60),i=n%60;return (e<=0?"+":"-")+$(r,2,"0")+":"+$(i,2,"0")},m:function t(e,n){if(e.date()<n.date())return -t(n,e);var r=12*(n.year()-e.year())+(n.month()-e.month()),i=e.clone().add(r,u),s=n-i<0,a=e.clone().add(r+(s?-1:1),u);return +(-(r+(n-i)/(s?i-a:a-i))||0)},a:function(t){return t<0?Math.ceil(t)||0:Math.floor(t)},p:function(h){return {M:u,y:o,w:s,d:i,D:f,h:r,m:n,s:e,ms:t,Q:a}[h]||String(h||"").toLowerCase().replace(/s$/,"")},u:function(t){return void 0===t}},y="en",M={};M[y]=d;var m=function(t){return t instanceof S},D=function(t,e,n){var r;if(!t)return y;if("string"==typeof t)M[t]&&(r=t),e&&(M[t]=e,r=t);else {var i=t.name;M[i]=t,r=i;}return !n&&r&&(y=r),r||!n&&y},v=function(t,e){if(m(t))return t.clone();var n="object"==typeof e?e:{};return n.date=t,n.args=arguments,new S(n)},g=l;g.l=D,g.i=m,g.w=function(t,e){return v(t,{locale:e.$L,utc:e.$u,x:e.$x,$offset:e.$offset})};var S=function(){function d(t){this.$L=this.$L||D(t.locale,null,!0),this.parse(t);}var $=d.prototype;return $.parse=function(t){this.$d=function(t){var e=t.date,n=t.utc;if(null===e)return new Date(NaN);if(g.u(e))return new Date;if(e instanceof Date)return new Date(e);if("string"==typeof e&&!/Z$/i.test(e)){var r=e.match(h);if(r){var i=r[2]-1||0,s=(r[7]||"0").substring(0,3);return n?new Date(Date.UTC(r[1],i,r[3]||1,r[4]||0,r[5]||0,r[6]||0,s)):new Date(r[1],i,r[3]||1,r[4]||0,r[5]||0,r[6]||0,s)}}return new Date(e)}(t),this.$x=t.x||{},this.init();},$.init=function(){var t=this.$d;this.$y=t.getFullYear(),this.$M=t.getMonth(),this.$D=t.getDate(),this.$W=t.getDay(),this.$H=t.getHours(),this.$m=t.getMinutes(),this.$s=t.getSeconds(),this.$ms=t.getMilliseconds();},$.$utils=function(){return g},$.isValid=function(){return !("Invalid Date"===this.$d.toString())},$.isSame=function(t,e){var n=v(t);return this.startOf(e)<=n&&n<=this.endOf(e)},$.isAfter=function(t,e){return v(t)<this.startOf(e)},$.isBefore=function(t,e){return this.endOf(e)<v(t)},$.$g=function(t,e,n){return g.u(t)?this[e]:this.set(n,t)},$.unix=function(){return Math.floor(this.valueOf()/1e3)},$.valueOf=function(){return this.$d.getTime()},$.startOf=function(t,a){var h=this,c=!!g.u(a)||a,d=g.p(t),$=function(t,e){var n=g.w(h.$u?Date.UTC(h.$y,e,t):new Date(h.$y,e,t),h);return c?n:n.endOf(i)},l=function(t,e){return g.w(h.toDate()[t].apply(h.toDate("s"),(c?[0,0,0,0]:[23,59,59,999]).slice(e)),h)},y=this.$W,M=this.$M,m=this.$D,D="set"+(this.$u?"UTC":"");switch(d){case o:return c?$(1,0):$(31,11);case u:return c?$(1,M):$(0,M+1);case s:var v=this.$locale().weekStart||0,S=(y<v?y+7:y)-v;return $(c?m-S:m+(6-S),M);case i:case f:return l(D+"Hours",0);case r:return l(D+"Minutes",1);case n:return l(D+"Seconds",2);case e:return l(D+"Milliseconds",3);default:return this.clone()}},$.endOf=function(t){return this.startOf(t,!1)},$.$set=function(s,a){var h,c=g.p(s),d="set"+(this.$u?"UTC":""),$=(h={},h[i]=d+"Date",h[f]=d+"Date",h[u]=d+"Month",h[o]=d+"FullYear",h[r]=d+"Hours",h[n]=d+"Minutes",h[e]=d+"Seconds",h[t]=d+"Milliseconds",h)[c],l=c===i?this.$D+(a-this.$W):a;if(c===u||c===o){var y=this.clone().set(f,1);y.$d[$](l),y.init(),this.$d=y.set(f,Math.min(this.$D,y.daysInMonth())).$d;}else $&&this.$d[$](l);return this.init(),this},$.set=function(t,e){return this.clone().$set(t,e)},$.get=function(t){return this[g.p(t)]()},$.add=function(t,a){var f,h=this;t=Number(t);var c=g.p(a),d=function(e){var n=v(h);return g.w(n.date(n.date()+Math.round(e*t)),h)};if(c===u)return this.set(u,this.$M+t);if(c===o)return this.set(o,this.$y+t);if(c===i)return d(1);if(c===s)return d(7);var $=(f={},f[n]=6e4,f[r]=36e5,f[e]=1e3,f)[c]||1,l=this.$d.getTime()+t*$;return g.w(l,this)},$.subtract=function(t,e){return this.add(-1*t,e)},$.format=function(t){var e=this;if(!this.isValid())return "Invalid Date";var n=t||"YYYY-MM-DDTHH:mm:ssZ",r=g.z(this),i=this.$locale(),s=this.$H,u=this.$m,a=this.$M,o=i.weekdays,f=i.months,h=function(t,r,i,s){return t&&(t[r]||t(e,n))||i[r].substr(0,s)},d=function(t){return g.s(s%12||12,t,"0")},$=i.meridiem||function(t,e,n){var r=t<12?"AM":"PM";return n?r.toLowerCase():r},l={YY:String(this.$y).slice(-2),YYYY:this.$y,M:a+1,MM:g.s(a+1,2,"0"),MMM:h(i.monthsShort,a,f,3),MMMM:h(f,a),D:this.$D,DD:g.s(this.$D,2,"0"),d:String(this.$W),dd:h(i.weekdaysMin,this.$W,o,2),ddd:h(i.weekdaysShort,this.$W,o,3),dddd:o[this.$W],H:String(s),HH:g.s(s,2,"0"),h:d(1),hh:d(2),a:$(s,u,!0),A:$(s,u,!1),m:String(u),mm:g.s(u,2,"0"),s:String(this.$s),ss:g.s(this.$s,2,"0"),SSS:g.s(this.$ms,3,"0"),Z:r};return n.replace(c,function(t,e){return e||l[t]||r.replace(":","")})},$.utcOffset=function(){return 15*-Math.round(this.$d.getTimezoneOffset()/15)},$.diff=function(t,f,h){var c,d=g.p(f),$=v(t),l=6e4*($.utcOffset()-this.utcOffset()),y=this-$,M=g.m(this,$);return M=(c={},c[o]=M/12,c[u]=M,c[a]=M/3,c[s]=(y-l)/6048e5,c[i]=(y-l)/864e5,c[r]=y/36e5,c[n]=y/6e4,c[e]=y/1e3,c)[d]||y,h?M:g.a(M)},$.daysInMonth=function(){return this.endOf(u).$D},$.$locale=function(){return M[this.$L]},$.locale=function(t,e){if(!t)return this.$L;var n=this.clone(),r=D(t,e,!0);return r&&(n.$L=r),n},$.clone=function(){return g.w(this.$d,this)},$.toDate=function(){return new Date(this.valueOf())},$.toJSON=function(){return this.isValid()?this.toISOString():null},$.toISOString=function(){return this.$d.toISOString()},$.toString=function(){return this.$d.toUTCString()},d}(),p=S.prototype;return v.prototype=p,[["$ms",t],["$s",e],["$m",n],["$H",r],["$W",i],["$M",u],["$y",o],["$D",f]].forEach(function(t){p[t[1]]=function(e){return this.$g(e,t[0],t[1])};}),v.extend=function(t,e){return t(e,S,v),v},v.locale=D,v.isDayjs=m,v.unix=function(t){return v(1e3*t)},v.en=M[y],v.Ls=M,v.p={},v});
    });

    var customParseFormat = createCommonjsModule(function (module, exports) {
    !function(t,e){module.exports=e();}(commonjsGlobal,function(){var t,e=/(\[[^[]*\])|([-:/.()\s]+)|(A|a|YYYY|YY?|MM?M?M?|Do|DD?|hh?|HH?|mm?|ss?|S{1,3}|z|ZZ?)/g,n=/\d\d/,r=/\d\d?/,o=/\d*[^\s\d-:/()]+/;var s=function(t){return function(e){this[t]=+e;}},i=[/[+-]\d\d:?\d\d/,function(t){var e,n;(this.zone||(this.zone={})).offset=(e=t.match(/([+-]|\d\d)/g),0===(n=60*e[1]+ +e[2])?0:"+"===e[0]?-n:n);}],a=function(e){var n=t[e];return n&&(n.indexOf?n:n.s.concat(n.f))},h={A:[/[AP]M/,function(t){this.afternoon="PM"===t;}],a:[/[ap]m/,function(t){this.afternoon="pm"===t;}],S:[/\d/,function(t){this.milliseconds=100*+t;}],SS:[n,function(t){this.milliseconds=10*+t;}],SSS:[/\d{3}/,function(t){this.milliseconds=+t;}],s:[r,s("seconds")],ss:[r,s("seconds")],m:[r,s("minutes")],mm:[r,s("minutes")],H:[r,s("hours")],h:[r,s("hours")],HH:[r,s("hours")],hh:[r,s("hours")],D:[r,s("day")],DD:[n,s("day")],Do:[o,function(e){var n=t.ordinal,r=e.match(/\d+/);if(this.day=r[0],n)for(var o=1;o<=31;o+=1)n(o).replace(/\[|\]/g,"")===e&&(this.day=o);}],M:[r,s("month")],MM:[n,s("month")],MMM:[o,function(t){var e=a("months"),n=(a("monthsShort")||e.map(function(t){return t.substr(0,3)})).indexOf(t)+1;if(n<1)throw new Error;this.month=n%12||n;}],MMMM:[o,function(t){var e=a("months").indexOf(t)+1;if(e<1)throw new Error;this.month=e%12||e;}],Y:[/[+-]?\d+/,s("year")],YY:[n,function(t){t=+t,this.year=t+(t>68?1900:2e3);}],YYYY:[/\d{4}/,s("year")],Z:i,ZZ:i};var f=function(t,n,r){try{var o=function(t){for(var n=t.match(e),r=n.length,o=0;o<r;o+=1){var s=n[o],i=h[s],a=i&&i[0],f=i&&i[1];n[o]=f?{regex:a,parser:f}:s.replace(/^\[|\]$/g,"");}return function(t){for(var e={},o=0,s=0;o<r;o+=1){var i=n[o];if("string"==typeof i)s+=i.length;else {var a=i.regex,h=i.parser,f=t.substr(s),u=a.exec(f)[0];h.call(e,u),t=t.replace(u,"");}}return function(t){var e=t.afternoon;if(void 0!==e){var n=t.hours;e?n<12&&(t.hours+=12):12===n&&(t.hours=0),delete t.afternoon;}}(e),e}}(n)(t),s=o.year,i=o.month,a=o.day,f=o.hours,u=o.minutes,c=o.seconds,d=o.milliseconds,l=o.zone,m=new Date,v=a||(s||i?1:m.getDate()),p=s||m.getFullYear(),y=0;s&&!i||(y=i>0?i-1:m.getMonth());var D=f||0,M=u||0,g=c||0,Y=d||0;return l?new Date(Date.UTC(p,y,v,D,M,g,Y+60*l.offset*1e3)):r?new Date(Date.UTC(p,y,v,D,M,g,Y)):new Date(p,y,v,D,M,g,Y)}catch(t){return new Date("")}};return function(e,n,r){r.p.customParseFormat=!0;var o=n.prototype,s=o.parse;o.parse=function(e){var n=e.date,o=e.utc,i=e.args;this.$u=o;var a=i[1];if("string"==typeof a){var h=!0===i[2],u=!0===i[3],c=h||u,d=i[2];u&&(d=i[2]),h||(t=d?r.Ls[d]:this.$locale()),this.$d=f(n,a,o),this.init(),d&&!0!==d&&(this.$L=this.locale(d).$L),c&&n!==this.format(a)&&(this.$d=new Date(""));}else if(a instanceof Array)for(var l=a.length,m=1;m<=l;m+=1){i[1]=a[m-1];var v=r.apply(this,i);if(v.isValid()){this.$d=v.$d,this.$L=v.$L,this.init();break}m===l&&(this.$d=new Date(""));}else s.call(this,e);};}});
    });

    var relativeTime = createCommonjsModule(function (module, exports) {
    !function(r,t){module.exports=t();}(commonjsGlobal,function(){return function(r,t,e){r=r||{};var n=t.prototype,o={future:"in %s",past:"%s ago",s:"a few seconds",m:"a minute",mm:"%d minutes",h:"an hour",hh:"%d hours",d:"a day",dd:"%d days",M:"a month",MM:"%d months",y:"a year",yy:"%d years"};e.en.relativeTime=o;var d=function(t,n,d,i){for(var u,a,s,f=d.$locale().relativeTime||o,l=r.thresholds||[{l:"s",r:44,d:"second"},{l:"m",r:89},{l:"mm",r:44,d:"minute"},{l:"h",r:89},{l:"hh",r:21,d:"hour"},{l:"d",r:35},{l:"dd",r:25,d:"day"},{l:"M",r:45},{l:"MM",r:10,d:"month"},{l:"y",r:17},{l:"yy",d:"year"}],h=l.length,m=0;m<h;m+=1){var c=l[m];c.d&&(u=i?e(t).diff(d,c.d,!0):d.diff(t,c.d,!0));var y=(r.rounding||Math.round)(Math.abs(u));if(s=u>0,y<=c.r||!c.r){y<=1&&m>0&&(c=l[m-1]);var p=f[c.l];a="string"==typeof p?p.replace("%d",y):p(y,n,c.l,s);break}}return n?a:(s?f.future:f.past).replace("%s",a)};n.to=function(r,t){return d(r,t,this,!0)},n.from=function(r,t){return d(r,t,this)};var i=function(r){return r.$u?e.utc():e()};n.toNow=function(r){return this.to(i(this),r)},n.fromNow=function(r){return this.from(i(this),r)};}});
    });

    var localizedFormat = createCommonjsModule(function (module, exports) {
    !function(e,t){module.exports=t();}(commonjsGlobal,function(){return function(e,t,o){var n=t.prototype,r=n.format,M={LTS:"h:mm:ss A",LT:"h:mm A",L:"MM/DD/YYYY",LL:"MMMM D, YYYY",LLL:"MMMM D, YYYY h:mm A",LLLL:"dddd, MMMM D, YYYY h:mm A"};o.en.formats=M,n.format=function(e){void 0===e&&(e="YYYY-MM-DDTHH:mm:ssZ");var t=this.$locale().formats,o=void 0===t?{}:t,n=e.replace(/(\[[^\]]+])|(LTS?|l{1,4}|L{1,4})/g,function(e,t,n){var r=n&&n.toUpperCase();return t||o[n]||M[n]||o[r].replace(/(\[[^\]]+])|(MMMM|MM|DD|dddd)/g,function(e,t,o){return t||o.slice(1)})});return r.call(this,n)};}});
    });

    var en$1 = createCommonjsModule(function (module, exports) {
    !function(e,n){module.exports=n();}(commonjsGlobal,function(){return {name:"en",weekdays:"Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday".split("_"),months:"January_February_March_April_May_June_July_August_September_October_November_December".split("_")}});
    });

    var fr = createCommonjsModule(function (module, exports) {
    !function(e,_){module.exports=_(dayjs_min);}(commonjsGlobal,function(e){e=e&&e.hasOwnProperty("default")?e.default:e;var _={name:"fr",weekdays:"dimanche_lundi_mardi_mercredi_jeudi_vendredi_samedi".split("_"),weekdaysShort:"dim._lun._mar._mer._jeu._ven._sam.".split("_"),weekdaysMin:"di_lu_ma_me_je_ve_sa".split("_"),months:"janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre".split("_"),monthsShort:"janv._févr._mars_avr._mai_juin_juil._août_sept._oct._nov._déc.".split("_"),weekStart:1,yearStart:4,formats:{LT:"HH:mm",LTS:"HH:mm:ss",L:"DD/MM/YYYY",LL:"D MMMM YYYY",LLL:"D MMMM YYYY HH:mm",LLLL:"dddd D MMMM YYYY HH:mm"},relativeTime:{future:"dans %s",past:"il y a %s",s:"quelques secondes",m:"une minute",mm:"%d minutes",h:"une heure",hh:"%d heures",d:"un jour",dd:"%d jours",M:"un mois",MM:"%d mois",y:"un an",yy:"%d ans"},ordinal:function(e){return ""+e+(1===e?"er":"")}};return e.locale(_,null,!0),_});
    });

    /* src/Status.svelte generated by Svelte v3.29.4 */
    const file$1 = "src/Status.svelte";

    function get_each_context(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[6] = list[i];
    	return child_ctx;
    }

    function get_each_context_1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[9] = list[i];
    	return child_ctx;
    }

    // (94:6) {#if status.author_category}
    function create_if_block_4(ctx) {
    	let span;
    	let t_value = /*status*/ ctx[1].author_category + "";
    	let t;

    	const block = {
    		c: function create() {
    			span = element("span");
    			t = text(t_value);
    			attr_dev(span, "class", "badge badge-primary");
    			add_location(span, file$1, 94, 6, 3508);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, span, anchor);
    			append_dev(span, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*status*/ 2 && t_value !== (t_value = /*status*/ ctx[1].author_category + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(span);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_4.name,
    		type: "if",
    		source: "(94:6) {#if status.author_category}",
    		ctx
    	});

    	return block;
    }

    // (97:6) {#if status.author_specialty}
    function create_if_block_3(ctx) {
    	let span;
    	let t_value = /*status*/ ctx[1].author_specialty + "";
    	let t;

    	const block = {
    		c: function create() {
    			span = element("span");
    			t = text(t_value);
    			attr_dev(span, "class", "badge badge-secondary");
    			add_location(span, file$1, 97, 6, 3628);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, span, anchor);
    			append_dev(span, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*status*/ 2 && t_value !== (t_value = /*status*/ ctx[1].author_specialty + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(span);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_3.name,
    		type: "if",
    		source: "(97:6) {#if status.author_specialty}",
    		ctx
    	});

    	return block;
    }

    // (102:6) {#if categoryOrTag(status) }
    function create_if_block(ctx) {
    	let div;
    	let t;
    	let if_block0 = /*status*/ ctx[1].status_category && create_if_block_2(ctx);
    	let if_block1 = /*status*/ ctx[1].status_tag && create_if_block_1(ctx);

    	const block = {
    		c: function create() {
    			div = element("div");
    			if (if_block0) if_block0.c();
    			t = space();
    			if (if_block1) if_block1.c();
    			attr_dev(div, "class", "mx-0 mt-0 mb-1");
    			add_location(div, file$1, 102, 6, 3807);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			if (if_block0) if_block0.m(div, null);
    			append_dev(div, t);
    			if (if_block1) if_block1.m(div, null);
    		},
    		p: function update(ctx, dirty) {
    			if (/*status*/ ctx[1].status_category) {
    				if (if_block0) {
    					if_block0.p(ctx, dirty);
    				} else {
    					if_block0 = create_if_block_2(ctx);
    					if_block0.c();
    					if_block0.m(div, t);
    				}
    			} else if (if_block0) {
    				if_block0.d(1);
    				if_block0 = null;
    			}

    			if (/*status*/ ctx[1].status_tag) {
    				if (if_block1) {
    					if_block1.p(ctx, dirty);
    				} else {
    					if_block1 = create_if_block_1(ctx);
    					if_block1.c();
    					if_block1.m(div, null);
    				}
    			} else if (if_block1) {
    				if_block1.d(1);
    				if_block1 = null;
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			if (if_block0) if_block0.d();
    			if (if_block1) if_block1.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block.name,
    		type: "if",
    		source: "(102:6) {#if categoryOrTag(status) }",
    		ctx
    	});

    	return block;
    }

    // (104:8) {#if status.status_category}
    function create_if_block_2(ctx) {
    	let each_1_anchor;
    	let each_value_1 = /*status*/ ctx[1].status_category;
    	validate_each_argument(each_value_1);
    	let each_blocks = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks[i] = create_each_block_1(get_each_context_1(ctx, each_value_1, i));
    	}

    	const block = {
    		c: function create() {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			each_1_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(target, anchor);
    			}

    			insert_dev(target, each_1_anchor, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*status*/ 2) {
    				each_value_1 = /*status*/ ctx[1].status_category;
    				validate_each_argument(each_value_1);
    				let i;

    				for (i = 0; i < each_value_1.length; i += 1) {
    					const child_ctx = get_each_context_1(ctx, each_value_1, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block_1(child_ctx);
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
    		d: function destroy(detaching) {
    			destroy_each(each_blocks, detaching);
    			if (detaching) detach_dev(each_1_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_2.name,
    		type: "if",
    		source: "(104:8) {#if status.status_category}",
    		ctx
    	});

    	return block;
    }

    // (105:8) {#each status.status_category as category}
    function create_each_block_1(ctx) {
    	let span;
    	let t_value = /*category*/ ctx[9] + "";
    	let t;

    	const block = {
    		c: function create() {
    			span = element("span");
    			t = text(t_value);
    			attr_dev(span, "class", "badge badge-pill badge-info mx-1");
    			add_location(span, file$1, 105, 8, 3932);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, span, anchor);
    			append_dev(span, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*status*/ 2 && t_value !== (t_value = /*category*/ ctx[9] + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(span);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_1.name,
    		type: "each",
    		source: "(105:8) {#each status.status_category as category}",
    		ctx
    	});

    	return block;
    }

    // (109:8) {#if status.status_tag}
    function create_if_block_1(ctx) {
    	let each_1_anchor;
    	let each_value = /*status*/ ctx[1].status_tag;
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block(get_each_context(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			each_1_anchor = empty();
    		},
    		m: function mount(target, anchor) {
    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(target, anchor);
    			}

    			insert_dev(target, each_1_anchor, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*status*/ 2) {
    				each_value = /*status*/ ctx[1].status_tag;
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(each_1_anchor.parentNode, each_1_anchor);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}
    		},
    		d: function destroy(detaching) {
    			destroy_each(each_blocks, detaching);
    			if (detaching) detach_dev(each_1_anchor);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1.name,
    		type: "if",
    		source: "(109:8) {#if status.status_tag}",
    		ctx
    	});

    	return block;
    }

    // (110:8) {#each status.status_tag as tag}
    function create_each_block(ctx) {
    	let span;
    	let t_value = /*tag*/ ctx[6] + "";
    	let t;

    	const block = {
    		c: function create() {
    			span = element("span");
    			t = text(t_value);
    			attr_dev(span, "class", "badge badge-pill badge-dark mx-1");
    			add_location(span, file$1, 110, 8, 4108);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, span, anchor);
    			append_dev(span, t);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*status*/ 2 && t_value !== (t_value = /*tag*/ ctx[6] + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(span);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block.name,
    		type: "each",
    		source: "(110:8) {#each status.status_tag as tag}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$1(ctx) {
    	let div4;
    	let div3;
    	let div0;
    	let img;
    	let img_src_value;
    	let t0;
    	let h60;
    	let span0;
    	let t1_value = /*status*/ ctx[1].user_name + "";
    	let t1;
    	let span1;
    	let t2;
    	let t3_value = /*status*/ ctx[1].user_screen_name + "";
    	let t3;
    	let t4;
    	let h61;
    	let t5;
    	let t6;
    	let p;
    	let t7_value = /*status*/ ctx[1].text + "";
    	let t7;
    	let t8;
    	let show_if = categoryOrTag(/*status*/ ctx[1]);
    	let t9;
    	let div2;
    	let span2;
    	let t10_value = /*fromNow*/ ctx[4](/*status*/ ctx[1].id_str) + "";
    	let t10;
    	let span2_title_value;
    	let t11;
    	let span3;
    	let a;
    	let t12_value = /*$_*/ ctx[2]("view_on_twitter") + "";
    	let t12;
    	let t13;
    	let div1;
    	let div1_title_value;
    	let a_href_value;
    	let a_aria_label_value;
    	let if_block0 = /*status*/ ctx[1].author_category && create_if_block_4(ctx);
    	let if_block1 = /*status*/ ctx[1].author_specialty && create_if_block_3(ctx);
    	let if_block2 = show_if && create_if_block(ctx);

    	const block = {
    		c: function create() {
    			div4 = element("div");
    			div3 = element("div");
    			div0 = element("div");
    			img = element("img");
    			t0 = space();
    			h60 = element("h6");
    			span0 = element("span");
    			t1 = text(t1_value);
    			span1 = element("span");
    			t2 = text("@");
    			t3 = text(t3_value);
    			t4 = space();
    			h61 = element("h6");
    			if (if_block0) if_block0.c();
    			t5 = space();
    			if (if_block1) if_block1.c();
    			t6 = space();
    			p = element("p");
    			t7 = text(t7_value);
    			t8 = space();
    			if (if_block2) if_block2.c();
    			t9 = space();
    			div2 = element("div");
    			span2 = element("span");
    			t10 = text(t10_value);
    			t11 = space();
    			span3 = element("span");
    			a = element("a");
    			t12 = text(t12_value);
    			t13 = space();
    			div1 = element("div");
    			attr_dev(img, "class", "rounded-circle profile-pic float-left pr-1 svelte-66b5vc");
    			if (img.src !== (img_src_value = "" + (/*baseURL*/ ctx[0] + /*status*/ ctx[1].avatar_normal))) attr_dev(img, "src", img_src_value);
    			attr_dev(img, "alt", "Profile pic");
    			add_location(img, file$1, 87, 8, 3122);
    			attr_dev(span0, "class", "name mx-1 svelte-66b5vc");
    			add_location(span0, file$1, 89, 10, 3277);
    			attr_dev(span1, "class", "screen_name mx-1 svelte-66b5vc");
    			add_location(span1, file$1, 89, 59, 3326);
    			attr_dev(h60, "class", "card-title");
    			add_location(h60, file$1, 88, 8, 3243);
    			add_location(div0, file$1, 86, 6, 3108);
    			attr_dev(h61, "class", "card-subtitle mb-2 text-muted");
    			add_location(h61, file$1, 92, 6, 3424);
    			attr_dev(p, "class", "card-text");
    			add_location(p, file$1, 100, 6, 3727);
    			attr_dev(span2, "class", "card-text");
    			attr_dev(span2, "data-toggle", "tooltip");
    			attr_dev(span2, "title", span2_title_value = /*dateTimeLocale*/ ctx[3](/*status*/ ctx[1].id_str));
    			add_location(span2, file$1, 116, 8, 4263);
    			attr_dev(div1, "class", "Icon Icon--twitter svelte-66b5vc");
    			attr_dev(div1, "title", div1_title_value = /*$_*/ ctx[2]("view_on_twitter"));
    			add_location(div1, file$1, 121, 8, 4586);
    			attr_dev(a, "href", a_href_value = "https://twitter.com/" + /*status*/ ctx[1].user_screen_name + "/status/" + /*status*/ ctx[1].id_str);
    			attr_dev(a, "class", "card-link");
    			attr_dev(a, "aria-label", a_aria_label_value = /*$_*/ ctx[2]("view_on_twitter"));
    			add_location(a, file$1, 119, 14, 4413);
    			add_location(span3, file$1, 119, 8, 4407);
    			attr_dev(div2, "class", "card-footer");
    			add_location(div2, file$1, 115, 6, 4229);
    			attr_dev(div3, "class", "card-body");
    			add_location(div3, file$1, 85, 4, 3078);
    			attr_dev(div4, "class", "card");
    			add_location(div4, file$1, 84, 0, 3055);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div4, anchor);
    			append_dev(div4, div3);
    			append_dev(div3, div0);
    			append_dev(div0, img);
    			append_dev(div0, t0);
    			append_dev(div0, h60);
    			append_dev(h60, span0);
    			append_dev(span0, t1);
    			append_dev(h60, span1);
    			append_dev(span1, t2);
    			append_dev(span1, t3);
    			append_dev(div3, t4);
    			append_dev(div3, h61);
    			if (if_block0) if_block0.m(h61, null);
    			append_dev(h61, t5);
    			if (if_block1) if_block1.m(h61, null);
    			append_dev(div3, t6);
    			append_dev(div3, p);
    			append_dev(p, t7);
    			append_dev(div3, t8);
    			if (if_block2) if_block2.m(div3, null);
    			append_dev(div3, t9);
    			append_dev(div3, div2);
    			append_dev(div2, span2);
    			append_dev(span2, t10);
    			append_dev(div2, t11);
    			append_dev(div2, span3);
    			append_dev(span3, a);
    			append_dev(a, t12);
    			append_dev(a, t13);
    			append_dev(a, div1);
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*baseURL, status*/ 3 && img.src !== (img_src_value = "" + (/*baseURL*/ ctx[0] + /*status*/ ctx[1].avatar_normal))) {
    				attr_dev(img, "src", img_src_value);
    			}

    			if (dirty & /*status*/ 2 && t1_value !== (t1_value = /*status*/ ctx[1].user_name + "")) set_data_dev(t1, t1_value);
    			if (dirty & /*status*/ 2 && t3_value !== (t3_value = /*status*/ ctx[1].user_screen_name + "")) set_data_dev(t3, t3_value);

    			if (/*status*/ ctx[1].author_category) {
    				if (if_block0) {
    					if_block0.p(ctx, dirty);
    				} else {
    					if_block0 = create_if_block_4(ctx);
    					if_block0.c();
    					if_block0.m(h61, t5);
    				}
    			} else if (if_block0) {
    				if_block0.d(1);
    				if_block0 = null;
    			}

    			if (/*status*/ ctx[1].author_specialty) {
    				if (if_block1) {
    					if_block1.p(ctx, dirty);
    				} else {
    					if_block1 = create_if_block_3(ctx);
    					if_block1.c();
    					if_block1.m(h61, null);
    				}
    			} else if (if_block1) {
    				if_block1.d(1);
    				if_block1 = null;
    			}

    			if (dirty & /*status*/ 2 && t7_value !== (t7_value = /*status*/ ctx[1].text + "")) set_data_dev(t7, t7_value);
    			if (dirty & /*status*/ 2) show_if = categoryOrTag(/*status*/ ctx[1]);

    			if (show_if) {
    				if (if_block2) {
    					if_block2.p(ctx, dirty);
    				} else {
    					if_block2 = create_if_block(ctx);
    					if_block2.c();
    					if_block2.m(div3, t9);
    				}
    			} else if (if_block2) {
    				if_block2.d(1);
    				if_block2 = null;
    			}

    			if (dirty & /*status*/ 2 && t10_value !== (t10_value = /*fromNow*/ ctx[4](/*status*/ ctx[1].id_str) + "")) set_data_dev(t10, t10_value);

    			if (dirty & /*status*/ 2 && span2_title_value !== (span2_title_value = /*dateTimeLocale*/ ctx[3](/*status*/ ctx[1].id_str))) {
    				attr_dev(span2, "title", span2_title_value);
    			}

    			if (dirty & /*$_*/ 4 && t12_value !== (t12_value = /*$_*/ ctx[2]("view_on_twitter") + "")) set_data_dev(t12, t12_value);

    			if (dirty & /*$_*/ 4 && div1_title_value !== (div1_title_value = /*$_*/ ctx[2]("view_on_twitter"))) {
    				attr_dev(div1, "title", div1_title_value);
    			}

    			if (dirty & /*status*/ 2 && a_href_value !== (a_href_value = "https://twitter.com/" + /*status*/ ctx[1].user_screen_name + "/status/" + /*status*/ ctx[1].id_str)) {
    				attr_dev(a, "href", a_href_value);
    			}

    			if (dirty & /*$_*/ 4 && a_aria_label_value !== (a_aria_label_value = /*$_*/ ctx[2]("view_on_twitter"))) {
    				attr_dev(a, "aria-label", a_aria_label_value);
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div4);
    			if (if_block0) if_block0.d();
    			if (if_block1) if_block1.d();
    			if (if_block2) if_block2.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$1.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function dateTime(id_str) {
    	let status_id = BigInt(id_str);
    	let offset = BigInt(1288834974657);
    	let timestamp = (status_id >> BigInt(22)) + offset;
    	var created_at = new Date(Number(timestamp));
    	return created_at;
    }

    function categoryOrTag(status) {
    	if (status.status_tag == null && status.status_category == null) {
    		return false;
    	}

    	if (status.status_tag.length == 0 && status.status_category.length == 0) {
    		return false;
    	} else {
    		return true;
    	}
    }

    function instance$1($$self, $$props, $$invalidate) {
    	let $_;
    	validate_store(nn, "_");
    	component_subscribe($$self, nn, $$value => $$invalidate(2, $_ = $$value));
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots("Status", slots, []);
    	dayjs_min.extend(customParseFormat);
    	dayjs_min.extend(relativeTime);
    	dayjs_min.extend(localizedFormat);

    	// we need to remove "-FR" from "fr-FR"
    	function setDayjsLocale() {
    		var extLocale = M();
    		var locale = extLocale.substring(0, extLocale.indexOf("-"));
    		dayjs_min.locale(locale); // use loaded locale globally
    	}

    	let { baseURL } = $$props;
    	let { status } = $$props;

    	onMount(() => {
    		setDayjsLocale();
    	});

    	function dateTimeLocale(id_str) {
    		var datetime = dateTime(id_str);
    		return dayjs_min(datetime).format("llll");
    	}

    	function fromNow(id_str) {
    		let dt = dateTime(id_str);
    		let dtFromNow = dayjs_min(dt).locale(M()).fromNow();
    		return dtFromNow;
    	}

    	const writable_props = ["baseURL", "status"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<Status> was created with unknown prop '${key}'`);
    	});

    	$$self.$$set = $$props => {
    		if ("baseURL" in $$props) $$invalidate(0, baseURL = $$props.baseURL);
    		if ("status" in $$props) $$invalidate(1, status = $$props.status);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		_: nn,
    		getLocaleFromNavigator: M,
    		dayjs: dayjs_min,
    		customParseFormat,
    		relativeTime,
    		localizedFormat,
    		setDayjsLocale,
    		baseURL,
    		status,
    		dateTimeLocale,
    		dateTime,
    		fromNow,
    		categoryOrTag,
    		$_
    	});

    	$$self.$inject_state = $$props => {
    		if ("baseURL" in $$props) $$invalidate(0, baseURL = $$props.baseURL);
    		if ("status" in $$props) $$invalidate(1, status = $$props.status);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [baseURL, status, $_, dateTimeLocale, fromNow];
    }

    class Status extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$1, create_fragment$1, safe_not_equal, { baseURL: 0, status: 1 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Status",
    			options,
    			id: create_fragment$1.name
    		});

    		const { ctx } = this.$$;
    		const props = options.props || {};

    		if (/*baseURL*/ ctx[0] === undefined && !("baseURL" in props)) {
    			console.warn("<Status> was created without expected prop 'baseURL'");
    		}

    		if (/*status*/ ctx[1] === undefined && !("status" in props)) {
    			console.warn("<Status> was created without expected prop 'status'");
    		}
    	}

    	get baseURL() {
    		throw new Error("<Status>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set baseURL(value) {
    		throw new Error("<Status>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get status() {
    		throw new Error("<Status>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set status(value) {
    		throw new Error("<Status>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/Categories.svelte generated by Svelte v3.29.4 */
    const file$2 = "src/Categories.svelte";

    function get_each_context$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[16] = list[i];
    	child_ctx[17] = list;
    	child_ctx[18] = i;
    	return child_ctx;
    }

    // (107:3) {#if id=="cat"}
    function create_if_block$1(ctx) {
    	let li;
    	let div;
    	let input;
    	let input_id_value;
    	let t0;
    	let label;
    	let bold;
    	let t1_value = /*$_*/ ctx[5]("select_all") + "";
    	let t1;
    	let label_for_value;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			li = element("li");
    			div = element("div");
    			input = element("input");
    			t0 = space();
    			label = element("label");
    			bold = element("bold");
    			t1 = text(t1_value);
    			attr_dev(input, "class", "custom-control-input");
    			attr_dev(input, "id", input_id_value = "checkAll" + /*id*/ ctx[2]);
    			attr_dev(input, "type", "checkbox");
    			add_location(input, file$2, 109, 5, 2626);
    			add_location(bold, file$2, 110, 77, 2829);
    			attr_dev(label, "class", "custom-control-label font-weight-bold");
    			attr_dev(label, "for", label_for_value = "checkAll" + /*id*/ ctx[2]);
    			add_location(label, file$2, 110, 5, 2757);
    			attr_dev(div, "class", "custom-control custom-checkbox");
    			add_location(div, file$2, 108, 3, 2576);
    			add_location(li, file$2, 107, 3, 2568);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, li, anchor);
    			append_dev(li, div);
    			append_dev(div, input);
    			input.checked = /*checkAll*/ ctx[4];
    			append_dev(div, t0);
    			append_dev(div, label);
    			append_dev(label, bold);
    			append_dev(bold, t1);

    			if (!mounted) {
    				dispose = [
    					listen_dev(input, "change", /*input_change_handler*/ ctx[8]),
    					listen_dev(input, "click", /*checkAllClicked*/ ctx[6], false, false, false)
    				];

    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*id*/ 4 && input_id_value !== (input_id_value = "checkAll" + /*id*/ ctx[2])) {
    				attr_dev(input, "id", input_id_value);
    			}

    			if (dirty & /*checkAll*/ 16) {
    				input.checked = /*checkAll*/ ctx[4];
    			}

    			if (dirty & /*$_*/ 32 && t1_value !== (t1_value = /*$_*/ ctx[5]("select_all") + "")) set_data_dev(t1, t1_value);

    			if (dirty & /*id*/ 4 && label_for_value !== (label_for_value = "checkAll" + /*id*/ ctx[2])) {
    				attr_dev(label, "for", label_for_value);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(li);
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$1.name,
    		type: "if",
    		source: "(107:3) {#if id==\\\"cat\\\"}",
    		ctx
    	});

    	return block;
    }

    // (115:3) {#each categories as category, i}
    function create_each_block$1(ctx) {
    	let li;
    	let div;
    	let input;
    	let input_id_value;
    	let input_value_value;
    	let t0;
    	let label;
    	let t1_value = /*category*/ ctx[16].tag + "";
    	let t1;
    	let label_for_value;
    	let t2;
    	let mounted;
    	let dispose;

    	function input_change_handler_1() {
    		/*input_change_handler_1*/ ctx[9].call(input, /*each_value*/ ctx[17], /*i*/ ctx[18]);
    	}

    	const block = {
    		c: function create() {
    			li = element("li");
    			div = element("div");
    			input = element("input");
    			t0 = space();
    			label = element("label");
    			t1 = text(t1_value);
    			t2 = space();
    			attr_dev(input, "class", "custom-control-input");
    			attr_dev(input, "id", input_id_value = "customCheck" + /*category*/ ctx[16].taggit_tag);
    			attr_dev(input, "type", "checkbox");
    			input.__value = input_value_value = /*category*/ ctx[16].taggit_tag;
    			input.value = input.__value;
    			/*$$binding_groups*/ ctx[10][0].push(input);
    			add_location(input, file$2, 117, 7, 2999);
    			attr_dev(label, "class", "custom-control-label");
    			attr_dev(label, "for", label_for_value = "customCheck" + /*category*/ ctx[16].taggit_tag);
    			add_location(label, file$2, 118, 7, 3194);
    			attr_dev(div, "class", "custom-control custom-checkbox");
    			add_location(div, file$2, 116, 5, 2947);
    			add_location(li, file$2, 115, 3, 2937);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, li, anchor);
    			append_dev(li, div);
    			append_dev(div, input);
    			input.checked = ~/*selected_categories*/ ctx[1].indexOf(input.__value);
    			input.checked = /*category*/ ctx[16].checked;
    			append_dev(div, t0);
    			append_dev(div, label);
    			append_dev(label, t1);
    			append_dev(li, t2);

    			if (!mounted) {
    				dispose = listen_dev(input, "change", input_change_handler_1);
    				mounted = true;
    			}
    		},
    		p: function update(new_ctx, dirty) {
    			ctx = new_ctx;

    			if (dirty & /*categories*/ 1 && input_id_value !== (input_id_value = "customCheck" + /*category*/ ctx[16].taggit_tag)) {
    				attr_dev(input, "id", input_id_value);
    			}

    			if (dirty & /*categories*/ 1 && input_value_value !== (input_value_value = /*category*/ ctx[16].taggit_tag)) {
    				prop_dev(input, "__value", input_value_value);
    				input.value = input.__value;
    			}

    			if (dirty & /*selected_categories*/ 2) {
    				input.checked = ~/*selected_categories*/ ctx[1].indexOf(input.__value);
    			}

    			if (dirty & /*categories*/ 1) {
    				input.checked = /*category*/ ctx[16].checked;
    			}

    			if (dirty & /*categories*/ 1 && t1_value !== (t1_value = /*category*/ ctx[16].tag + "")) set_data_dev(t1, t1_value);

    			if (dirty & /*categories*/ 1 && label_for_value !== (label_for_value = "customCheck" + /*category*/ ctx[16].taggit_tag)) {
    				attr_dev(label, "for", label_for_value);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(li);
    			/*$$binding_groups*/ ctx[10][0].splice(/*$$binding_groups*/ ctx[10][0].indexOf(input), 1);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$1.name,
    		type: "each",
    		source: "(115:3) {#each categories as category, i}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$2(ctx) {
    	let div2;
    	let div1;
    	let div0;
    	let h2;
    	let t0;
    	let t1;
    	let ul;
    	let t2;
    	let if_block = /*id*/ ctx[2] == "cat" && create_if_block$1(ctx);
    	let each_value = /*categories*/ ctx[0];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$1(get_each_context$1(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			div2 = element("div");
    			div1 = element("div");
    			div0 = element("div");
    			h2 = element("h2");
    			t0 = text(/*title*/ ctx[3]);
    			t1 = space();
    			ul = element("ul");
    			if (if_block) if_block.c();
    			t2 = space();

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			add_location(h2, file$2, 104, 2, 2521);
    			attr_dev(ul, "class", "svelte-1c8lruv");
    			add_location(ul, file$2, 105, 3, 2541);
    			attr_dev(div0, "class", "col-md-auto");
    			add_location(div0, file$2, 103, 2, 2493);
    			attr_dev(div1, "class", "row");
    			add_location(div1, file$2, 102, 1, 2473);
    			attr_dev(div2, "class", "container");
    			add_location(div2, file$2, 101, 0, 2448);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div2, anchor);
    			append_dev(div2, div1);
    			append_dev(div1, div0);
    			append_dev(div0, h2);
    			append_dev(h2, t0);
    			append_dev(div0, t1);
    			append_dev(div0, ul);
    			if (if_block) if_block.m(ul, null);
    			append_dev(ul, t2);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(ul, null);
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*title*/ 8) set_data_dev(t0, /*title*/ ctx[3]);

    			if (/*id*/ ctx[2] == "cat") {
    				if (if_block) {
    					if_block.p(ctx, dirty);
    				} else {
    					if_block = create_if_block$1(ctx);
    					if_block.c();
    					if_block.m(ul, t2);
    				}
    			} else if (if_block) {
    				if_block.d(1);
    				if_block = null;
    			}

    			if (dirty & /*categories, selected_categories*/ 3) {
    				each_value = /*categories*/ ctx[0];
    				validate_each_argument(each_value);
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
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div2);
    			if (if_block) if_block.d();
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$2.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function arrayRemove(arr, value) {
    	return arr.filter(function (ele) {
    		return ele != value;
    	});
    }

    function instance$2($$self, $$props, $$invalidate) {
    	let $_;
    	validate_store(nn, "_");
    	component_subscribe($$self, nn, $$value => $$invalidate(5, $_ = $$value));
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots("Categories", slots, []);
    	let { id } = $$props;
    	let { title } = $$props;
    	let { categories = [] } = $$props;
    	let { selected_categories } = $$props;
    	let cat_length = 0;
    	let checkAll = true;
    	let { query = "" } = $$props;

    	function addCheckedToSelected(bool) {
    		for (var i = 0; i < categories.length; i++) {
    			$$invalidate(0, categories[i].checked = bool, categories);
    			let tagit = categories[i].taggit_tag;

    			if (selected_categories.includes(tagit) == false && bool) {
    				selected_categories.push(tagit);
    			} else if (selected_categories.includes(tagit) == true && bool == false) {
    				$$invalidate(1, selected_categories = arrayRemove(selected_categories, tagit));
    			}
    		}
    	}

    	function setAllCheckboxesTo(bool) {
    		for (var i = 0; i < categories.length; i++) {
    			$$invalidate(0, categories[i].checked = bool, categories);
    		}

    		addCheckedToSelected(bool);
    	}

    	function checkedCount() {
    		let count = 0;

    		for (var i = 0; i < categories.length; i++) {
    			if (categories[i].checked === true) {
    				count += 1;
    			}
    		}

    		return count;
    	}

    	function checkAllClicked() {
    		//console.log(`total: ${categories.length}`);
    		//console.log(`selected: ${selected_categories.length}`);
    		if (selected_categories.length < categories.length) {
    			setAllCheckboxesTo(true);

    			//console.log(`total: ${categories.length}`);
    			//console.log(`selected: ${selected_categories.length}`);
    			$$invalidate(4, checkAll = true);
    		} else if (selected_categories.length == categories.length) {
    			if (selected_categories.length == 0) {
    				setAllCheckboxesTo(true);
    			} else //console.log(`selected: ${selected_categories.length}`);
    			{
    				setAllCheckboxesTo(false); //console.log(`total: ${categories.length}`);
    			} //console.log(`total: ${categories.length}`);
    			//console.log(`selected: ${selected_categories.length}`);
    		}
    	}

    	function buildQuery() {
    		let q = "&";

    		for (let i = 0; i < selected_categories.length; i++) {
    			q = q + `tag=${selected_categories[i]}`;

    			if (i < selected_categories.length - 1) {
    				q = q + "&";
    			}
    		}

    		//console.log(`query: ${q}`);
    		return q;
    	}

    	const writable_props = ["id", "title", "categories", "selected_categories", "query"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<Categories> was created with unknown prop '${key}'`);
    	});

    	const $$binding_groups = [[]];

    	function input_change_handler() {
    		checkAll = this.checked;
    		(($$invalidate(4, checkAll), $$invalidate(1, selected_categories)), $$invalidate(0, categories));
    	}

    	function input_change_handler_1(each_value, i) {
    		selected_categories = get_binding_group_value($$binding_groups[0], this.__value, this.checked);
    		each_value[i].checked = this.checked;
    		$$invalidate(1, selected_categories);
    		$$invalidate(0, categories);
    	}

    	$$self.$$set = $$props => {
    		if ("id" in $$props) $$invalidate(2, id = $$props.id);
    		if ("title" in $$props) $$invalidate(3, title = $$props.title);
    		if ("categories" in $$props) $$invalidate(0, categories = $$props.categories);
    		if ("selected_categories" in $$props) $$invalidate(1, selected_categories = $$props.selected_categories);
    		if ("query" in $$props) $$invalidate(7, query = $$props.query);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		_: nn,
    		id,
    		title,
    		categories,
    		selected_categories,
    		cat_length,
    		checkAll,
    		query,
    		arrayRemove,
    		addCheckedToSelected,
    		setAllCheckboxesTo,
    		checkedCount,
    		checkAllClicked,
    		buildQuery,
    		$_
    	});

    	$$self.$inject_state = $$props => {
    		if ("id" in $$props) $$invalidate(2, id = $$props.id);
    		if ("title" in $$props) $$invalidate(3, title = $$props.title);
    		if ("categories" in $$props) $$invalidate(0, categories = $$props.categories);
    		if ("selected_categories" in $$props) $$invalidate(1, selected_categories = $$props.selected_categories);
    		if ("cat_length" in $$props) cat_length = $$props.cat_length;
    		if ("checkAll" in $$props) $$invalidate(4, checkAll = $$props.checkAll);
    		if ("query" in $$props) $$invalidate(7, query = $$props.query);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*selected_categories, categories*/ 3) {
    			 if (selected_categories.length == categories.length) {
    				$$invalidate(4, checkAll = true);
    			}
    		}

    		if ($$self.$$.dirty & /*selected_categories, categories*/ 3) {
    			 if (selected_categories.length < categories.length) {
    				$$invalidate(4, checkAll = false);
    			}
    		}

    		if ($$self.$$.dirty & /*selected_categories*/ 2) {
    			 if (selected_categories.length > 0) {
    				$$invalidate(7, query = buildQuery());
    			} else {
    				$$invalidate(7, query = "");
    			}
    		}
    	};

    	return [
    		categories,
    		selected_categories,
    		id,
    		title,
    		checkAll,
    		$_,
    		checkAllClicked,
    		query,
    		input_change_handler,
    		input_change_handler_1,
    		$$binding_groups
    	];
    }

    class Categories extends SvelteComponentDev {
    	constructor(options) {
    		super(options);

    		init(this, options, instance$2, create_fragment$2, safe_not_equal, {
    			id: 2,
    			title: 3,
    			categories: 0,
    			selected_categories: 1,
    			query: 7
    		});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Categories",
    			options,
    			id: create_fragment$2.name
    		});

    		const { ctx } = this.$$;
    		const props = options.props || {};

    		if (/*id*/ ctx[2] === undefined && !("id" in props)) {
    			console.warn("<Categories> was created without expected prop 'id'");
    		}

    		if (/*title*/ ctx[3] === undefined && !("title" in props)) {
    			console.warn("<Categories> was created without expected prop 'title'");
    		}

    		if (/*selected_categories*/ ctx[1] === undefined && !("selected_categories" in props)) {
    			console.warn("<Categories> was created without expected prop 'selected_categories'");
    		}
    	}

    	get id() {
    		throw new Error("<Categories>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set id(value) {
    		throw new Error("<Categories>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get title() {
    		throw new Error("<Categories>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set title(value) {
    		throw new Error("<Categories>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get categories() {
    		throw new Error("<Categories>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set categories(value) {
    		throw new Error("<Categories>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get selected_categories() {
    		throw new Error("<Categories>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set selected_categories(value) {
    		throw new Error("<Categories>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get query() {
    		throw new Error("<Categories>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set query(value) {
    		throw new Error("<Categories>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    /* src/FlatpickrCss.svelte generated by Svelte v3.29.4 */

    function create_fragment$3(ctx) {
    	const block = {
    		c: noop,
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: noop,
    		p: noop,
    		i: noop,
    		o: noop,
    		d: noop
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$3.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$3($$self, $$props) {
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots("FlatpickrCss", slots, []);
    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<FlatpickrCss> was created with unknown prop '${key}'`);
    	});

    	return [];
    }

    class FlatpickrCss extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$3, create_fragment$3, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "FlatpickrCss",
    			options,
    			id: create_fragment$3.name
    		});
    	}
    }

    var flatpickr = createCommonjsModule(function (module, exports) {
    /* flatpickr v4.6.6, @license MIT */
    (function (global, factory) {
         module.exports = factory() ;
    }(commonjsGlobal, (function () {
        /*! *****************************************************************************
        Copyright (c) Microsoft Corporation.

        Permission to use, copy, modify, and/or distribute this software for any
        purpose with or without fee is hereby granted.

        THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
        REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
        AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
        INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
        LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
        OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
        PERFORMANCE OF THIS SOFTWARE.
        ***************************************************************************** */

        var __assign = function() {
            __assign = Object.assign || function __assign(t) {
                for (var s, i = 1, n = arguments.length; i < n; i++) {
                    s = arguments[i];
                    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
                }
                return t;
            };
            return __assign.apply(this, arguments);
        };

        function __spreadArrays() {
            for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
            for (var r = Array(s), k = 0, i = 0; i < il; i++)
                for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
                    r[k] = a[j];
            return r;
        }

        var HOOKS = [
            "onChange",
            "onClose",
            "onDayCreate",
            "onDestroy",
            "onKeyDown",
            "onMonthChange",
            "onOpen",
            "onParseConfig",
            "onReady",
            "onValueUpdate",
            "onYearChange",
            "onPreCalendarPosition",
        ];
        var defaults = {
            _disable: [],
            _enable: [],
            allowInput: false,
            allowInvalidPreload: false,
            altFormat: "F j, Y",
            altInput: false,
            altInputClass: "form-control input",
            animate: typeof window === "object" &&
                window.navigator.userAgent.indexOf("MSIE") === -1,
            ariaDateFormat: "F j, Y",
            autoFillDefaultTime: true,
            clickOpens: true,
            closeOnSelect: true,
            conjunction: ", ",
            dateFormat: "Y-m-d",
            defaultHour: 12,
            defaultMinute: 0,
            defaultSeconds: 0,
            disable: [],
            disableMobile: false,
            enable: [],
            enableSeconds: false,
            enableTime: false,
            errorHandler: function (err) {
                return typeof console !== "undefined" && console.warn(err);
            },
            getWeek: function (givenDate) {
                var date = new Date(givenDate.getTime());
                date.setHours(0, 0, 0, 0);
                // Thursday in current week decides the year.
                date.setDate(date.getDate() + 3 - ((date.getDay() + 6) % 7));
                // January 4 is always in week 1.
                var week1 = new Date(date.getFullYear(), 0, 4);
                // Adjust to Thursday in week 1 and count number of weeks from date to week1.
                return (1 +
                    Math.round(((date.getTime() - week1.getTime()) / 86400000 -
                        3 +
                        ((week1.getDay() + 6) % 7)) /
                        7));
            },
            hourIncrement: 1,
            ignoredFocusElements: [],
            inline: false,
            locale: "default",
            minuteIncrement: 5,
            mode: "single",
            monthSelectorType: "dropdown",
            nextArrow: "<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 17 17'><g></g><path d='M13.207 8.472l-7.854 7.854-0.707-0.707 7.146-7.146-7.146-7.148 0.707-0.707 7.854 7.854z' /></svg>",
            noCalendar: false,
            now: new Date(),
            onChange: [],
            onClose: [],
            onDayCreate: [],
            onDestroy: [],
            onKeyDown: [],
            onMonthChange: [],
            onOpen: [],
            onParseConfig: [],
            onReady: [],
            onValueUpdate: [],
            onYearChange: [],
            onPreCalendarPosition: [],
            plugins: [],
            position: "auto",
            positionElement: undefined,
            prevArrow: "<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 17 17'><g></g><path d='M5.207 8.471l7.146 7.147-0.707 0.707-7.853-7.854 7.854-7.853 0.707 0.707-7.147 7.146z' /></svg>",
            shorthandCurrentMonth: false,
            showMonths: 1,
            static: false,
            time_24hr: false,
            weekNumbers: false,
            wrap: false,
        };

        var english = {
            weekdays: {
                shorthand: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                longhand: [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ],
            },
            months: {
                shorthand: [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ],
                longhand: [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ],
            },
            daysInMonth: [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
            firstDayOfWeek: 0,
            ordinal: function (nth) {
                var s = nth % 100;
                if (s > 3 && s < 21)
                    return "th";
                switch (s % 10) {
                    case 1:
                        return "st";
                    case 2:
                        return "nd";
                    case 3:
                        return "rd";
                    default:
                        return "th";
                }
            },
            rangeSeparator: " to ",
            weekAbbreviation: "Wk",
            scrollTitle: "Scroll to increment",
            toggleTitle: "Click to toggle",
            amPM: ["AM", "PM"],
            yearAriaLabel: "Year",
            monthAriaLabel: "Month",
            hourAriaLabel: "Hour",
            minuteAriaLabel: "Minute",
            time_24hr: false,
        };

        var pad = function (number, length) {
            if (length === void 0) { length = 2; }
            return ("000" + number).slice(length * -1);
        };
        var int = function (bool) { return (bool === true ? 1 : 0); };
        /* istanbul ignore next */
        function debounce(func, wait, immediate) {
            if (immediate === void 0) { immediate = false; }
            var timeout;
            return function () {
                var context = this, args = arguments;
                timeout !== null && clearTimeout(timeout);
                timeout = window.setTimeout(function () {
                    timeout = null;
                    if (!immediate)
                        func.apply(context, args);
                }, wait);
                if (immediate && !timeout)
                    func.apply(context, args);
            };
        }
        var arrayify = function (obj) {
            return obj instanceof Array ? obj : [obj];
        };

        function toggleClass(elem, className, bool) {
            if (bool === true)
                return elem.classList.add(className);
            elem.classList.remove(className);
        }
        function createElement(tag, className, content) {
            var e = window.document.createElement(tag);
            className = className || "";
            content = content || "";
            e.className = className;
            if (content !== undefined)
                e.textContent = content;
            return e;
        }
        function clearNode(node) {
            while (node.firstChild)
                node.removeChild(node.firstChild);
        }
        function findParent(node, condition) {
            if (condition(node))
                return node;
            else if (node.parentNode)
                return findParent(node.parentNode, condition);
            return undefined; // nothing found
        }
        function createNumberInput(inputClassName, opts) {
            var wrapper = createElement("div", "numInputWrapper"), numInput = createElement("input", "numInput " + inputClassName), arrowUp = createElement("span", "arrowUp"), arrowDown = createElement("span", "arrowDown");
            if (navigator.userAgent.indexOf("MSIE 9.0") === -1) {
                numInput.type = "number";
            }
            else {
                numInput.type = "text";
                numInput.pattern = "\\d*";
            }
            if (opts !== undefined)
                for (var key in opts)
                    numInput.setAttribute(key, opts[key]);
            wrapper.appendChild(numInput);
            wrapper.appendChild(arrowUp);
            wrapper.appendChild(arrowDown);
            return wrapper;
        }
        function getEventTarget(event) {
            try {
                if (typeof event.composedPath === "function") {
                    var path = event.composedPath();
                    return path[0];
                }
                return event.target;
            }
            catch (error) {
                return event.target;
            }
        }

        var doNothing = function () { return undefined; };
        var monthToStr = function (monthNumber, shorthand, locale) { return locale.months[shorthand ? "shorthand" : "longhand"][monthNumber]; };
        var revFormat = {
            D: doNothing,
            F: function (dateObj, monthName, locale) {
                dateObj.setMonth(locale.months.longhand.indexOf(monthName));
            },
            G: function (dateObj, hour) {
                dateObj.setHours(parseFloat(hour));
            },
            H: function (dateObj, hour) {
                dateObj.setHours(parseFloat(hour));
            },
            J: function (dateObj, day) {
                dateObj.setDate(parseFloat(day));
            },
            K: function (dateObj, amPM, locale) {
                dateObj.setHours((dateObj.getHours() % 12) +
                    12 * int(new RegExp(locale.amPM[1], "i").test(amPM)));
            },
            M: function (dateObj, shortMonth, locale) {
                dateObj.setMonth(locale.months.shorthand.indexOf(shortMonth));
            },
            S: function (dateObj, seconds) {
                dateObj.setSeconds(parseFloat(seconds));
            },
            U: function (_, unixSeconds) { return new Date(parseFloat(unixSeconds) * 1000); },
            W: function (dateObj, weekNum, locale) {
                var weekNumber = parseInt(weekNum);
                var date = new Date(dateObj.getFullYear(), 0, 2 + (weekNumber - 1) * 7, 0, 0, 0, 0);
                date.setDate(date.getDate() - date.getDay() + locale.firstDayOfWeek);
                return date;
            },
            Y: function (dateObj, year) {
                dateObj.setFullYear(parseFloat(year));
            },
            Z: function (_, ISODate) { return new Date(ISODate); },
            d: function (dateObj, day) {
                dateObj.setDate(parseFloat(day));
            },
            h: function (dateObj, hour) {
                dateObj.setHours(parseFloat(hour));
            },
            i: function (dateObj, minutes) {
                dateObj.setMinutes(parseFloat(minutes));
            },
            j: function (dateObj, day) {
                dateObj.setDate(parseFloat(day));
            },
            l: doNothing,
            m: function (dateObj, month) {
                dateObj.setMonth(parseFloat(month) - 1);
            },
            n: function (dateObj, month) {
                dateObj.setMonth(parseFloat(month) - 1);
            },
            s: function (dateObj, seconds) {
                dateObj.setSeconds(parseFloat(seconds));
            },
            u: function (_, unixMillSeconds) {
                return new Date(parseFloat(unixMillSeconds));
            },
            w: doNothing,
            y: function (dateObj, year) {
                dateObj.setFullYear(2000 + parseFloat(year));
            },
        };
        var tokenRegex = {
            D: "(\\w+)",
            F: "(\\w+)",
            G: "(\\d\\d|\\d)",
            H: "(\\d\\d|\\d)",
            J: "(\\d\\d|\\d)\\w+",
            K: "",
            M: "(\\w+)",
            S: "(\\d\\d|\\d)",
            U: "(.+)",
            W: "(\\d\\d|\\d)",
            Y: "(\\d{4})",
            Z: "(.+)",
            d: "(\\d\\d|\\d)",
            h: "(\\d\\d|\\d)",
            i: "(\\d\\d|\\d)",
            j: "(\\d\\d|\\d)",
            l: "(\\w+)",
            m: "(\\d\\d|\\d)",
            n: "(\\d\\d|\\d)",
            s: "(\\d\\d|\\d)",
            u: "(.+)",
            w: "(\\d\\d|\\d)",
            y: "(\\d{2})",
        };
        var formats = {
            // get the date in UTC
            Z: function (date) { return date.toISOString(); },
            // weekday name, short, e.g. Thu
            D: function (date, locale, options) {
                return locale.weekdays.shorthand[formats.w(date, locale, options)];
            },
            // full month name e.g. January
            F: function (date, locale, options) {
                return monthToStr(formats.n(date, locale, options) - 1, false, locale);
            },
            // padded hour 1-12
            G: function (date, locale, options) {
                return pad(formats.h(date, locale, options));
            },
            // hours with leading zero e.g. 03
            H: function (date) { return pad(date.getHours()); },
            // day (1-30) with ordinal suffix e.g. 1st, 2nd
            J: function (date, locale) {
                return locale.ordinal !== undefined
                    ? date.getDate() + locale.ordinal(date.getDate())
                    : date.getDate();
            },
            // AM/PM
            K: function (date, locale) { return locale.amPM[int(date.getHours() > 11)]; },
            // shorthand month e.g. Jan, Sep, Oct, etc
            M: function (date, locale) {
                return monthToStr(date.getMonth(), true, locale);
            },
            // seconds 00-59
            S: function (date) { return pad(date.getSeconds()); },
            // unix timestamp
            U: function (date) { return date.getTime() / 1000; },
            W: function (date, _, options) {
                return options.getWeek(date);
            },
            // full year e.g. 2016, padded (0001-9999)
            Y: function (date) { return pad(date.getFullYear(), 4); },
            // day in month, padded (01-30)
            d: function (date) { return pad(date.getDate()); },
            // hour from 1-12 (am/pm)
            h: function (date) { return (date.getHours() % 12 ? date.getHours() % 12 : 12); },
            // minutes, padded with leading zero e.g. 09
            i: function (date) { return pad(date.getMinutes()); },
            // day in month (1-30)
            j: function (date) { return date.getDate(); },
            // weekday name, full, e.g. Thursday
            l: function (date, locale) {
                return locale.weekdays.longhand[date.getDay()];
            },
            // padded month number (01-12)
            m: function (date) { return pad(date.getMonth() + 1); },
            // the month number (1-12)
            n: function (date) { return date.getMonth() + 1; },
            // seconds 0-59
            s: function (date) { return date.getSeconds(); },
            // Unix Milliseconds
            u: function (date) { return date.getTime(); },
            // number of the day of the week
            w: function (date) { return date.getDay(); },
            // last two digits of year e.g. 16 for 2016
            y: function (date) { return String(date.getFullYear()).substring(2); },
        };

        var createDateFormatter = function (_a) {
            var _b = _a.config, config = _b === void 0 ? defaults : _b, _c = _a.l10n, l10n = _c === void 0 ? english : _c, _d = _a.isMobile, isMobile = _d === void 0 ? false : _d;
            return function (dateObj, frmt, overrideLocale) {
                var locale = overrideLocale || l10n;
                if (config.formatDate !== undefined && !isMobile) {
                    return config.formatDate(dateObj, frmt, locale);
                }
                return frmt
                    .split("")
                    .map(function (c, i, arr) {
                    return formats[c] && arr[i - 1] !== "\\"
                        ? formats[c](dateObj, locale, config)
                        : c !== "\\"
                            ? c
                            : "";
                })
                    .join("");
            };
        };
        var createDateParser = function (_a) {
            var _b = _a.config, config = _b === void 0 ? defaults : _b, _c = _a.l10n, l10n = _c === void 0 ? english : _c;
            return function (date, givenFormat, timeless, customLocale) {
                if (date !== 0 && !date)
                    return undefined;
                var locale = customLocale || l10n;
                var parsedDate;
                var dateOrig = date;
                if (date instanceof Date)
                    parsedDate = new Date(date.getTime());
                else if (typeof date !== "string" &&
                    date.toFixed !== undefined // timestamp
                )
                    // create a copy
                    parsedDate = new Date(date);
                else if (typeof date === "string") {
                    // date string
                    var format = givenFormat || (config || defaults).dateFormat;
                    var datestr = String(date).trim();
                    if (datestr === "today") {
                        parsedDate = new Date();
                        timeless = true;
                    }
                    else if (/Z$/.test(datestr) ||
                        /GMT$/.test(datestr) // datestrings w/ timezone
                    )
                        parsedDate = new Date(date);
                    else if (config && config.parseDate)
                        parsedDate = config.parseDate(date, format);
                    else {
                        parsedDate =
                            !config || !config.noCalendar
                                ? new Date(new Date().getFullYear(), 0, 1, 0, 0, 0, 0)
                                : new Date(new Date().setHours(0, 0, 0, 0));
                        var matched = void 0, ops = [];
                        for (var i = 0, matchIndex = 0, regexStr = ""; i < format.length; i++) {
                            var token_1 = format[i];
                            var isBackSlash = token_1 === "\\";
                            var escaped = format[i - 1] === "\\" || isBackSlash;
                            if (tokenRegex[token_1] && !escaped) {
                                regexStr += tokenRegex[token_1];
                                var match = new RegExp(regexStr).exec(date);
                                if (match && (matched = true)) {
                                    ops[token_1 !== "Y" ? "push" : "unshift"]({
                                        fn: revFormat[token_1],
                                        val: match[++matchIndex],
                                    });
                                }
                            }
                            else if (!isBackSlash)
                                regexStr += "."; // don't really care
                            ops.forEach(function (_a) {
                                var fn = _a.fn, val = _a.val;
                                return (parsedDate = fn(parsedDate, val, locale) || parsedDate);
                            });
                        }
                        parsedDate = matched ? parsedDate : undefined;
                    }
                }
                /* istanbul ignore next */
                if (!(parsedDate instanceof Date && !isNaN(parsedDate.getTime()))) {
                    config.errorHandler(new Error("Invalid date provided: " + dateOrig));
                    return undefined;
                }
                if (timeless === true)
                    parsedDate.setHours(0, 0, 0, 0);
                return parsedDate;
            };
        };
        /**
         * Compute the difference in dates, measured in ms
         */
        function compareDates(date1, date2, timeless) {
            if (timeless === void 0) { timeless = true; }
            if (timeless !== false) {
                return (new Date(date1.getTime()).setHours(0, 0, 0, 0) -
                    new Date(date2.getTime()).setHours(0, 0, 0, 0));
            }
            return date1.getTime() - date2.getTime();
        }
        var isBetween = function (ts, ts1, ts2) {
            return ts > Math.min(ts1, ts2) && ts < Math.max(ts1, ts2);
        };
        var duration = {
            DAY: 86400000,
        };

        if (typeof Object.assign !== "function") {
            Object.assign = function (target) {
                var args = [];
                for (var _i = 1; _i < arguments.length; _i++) {
                    args[_i - 1] = arguments[_i];
                }
                if (!target) {
                    throw TypeError("Cannot convert undefined or null to object");
                }
                var _loop_1 = function (source) {
                    if (source) {
                        Object.keys(source).forEach(function (key) { return (target[key] = source[key]); });
                    }
                };
                for (var _a = 0, args_1 = args; _a < args_1.length; _a++) {
                    var source = args_1[_a];
                    _loop_1(source);
                }
                return target;
            };
        }

        var DEBOUNCED_CHANGE_MS = 300;
        function FlatpickrInstance(element, instanceConfig) {
            var self = {
                config: __assign(__assign({}, defaults), flatpickr.defaultConfig),
                l10n: english,
            };
            self.parseDate = createDateParser({ config: self.config, l10n: self.l10n });
            self._handlers = [];
            self.pluginElements = [];
            self.loadedPlugins = [];
            self._bind = bind;
            self._setHoursFromDate = setHoursFromDate;
            self._positionCalendar = positionCalendar;
            self.changeMonth = changeMonth;
            self.changeYear = changeYear;
            self.clear = clear;
            self.close = close;
            self._createElement = createElement;
            self.destroy = destroy;
            self.isEnabled = isEnabled;
            self.jumpToDate = jumpToDate;
            self.open = open;
            self.redraw = redraw;
            self.set = set;
            self.setDate = setDate;
            self.toggle = toggle;
            function setupHelperFunctions() {
                self.utils = {
                    getDaysInMonth: function (month, yr) {
                        if (month === void 0) { month = self.currentMonth; }
                        if (yr === void 0) { yr = self.currentYear; }
                        if (month === 1 && ((yr % 4 === 0 && yr % 100 !== 0) || yr % 400 === 0))
                            return 29;
                        return self.l10n.daysInMonth[month];
                    },
                };
            }
            function init() {
                self.element = self.input = element;
                self.isOpen = false;
                parseConfig();
                setupLocale();
                setupInputs();
                setupDates();
                setupHelperFunctions();
                if (!self.isMobile)
                    build();
                bindEvents();
                if (self.selectedDates.length || self.config.noCalendar) {
                    if (self.config.enableTime) {
                        setHoursFromDate(self.config.noCalendar
                            ? self.latestSelectedDateObj || self.config.minDate
                            : undefined);
                    }
                    updateValue(false);
                }
                setCalendarWidth();
                var isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
                /* TODO: investigate this further
            
                  Currently, there is weird positioning behavior in safari causing pages
                  to scroll up. https://github.com/chmln/flatpickr/issues/563
            
                  However, most browsers are not Safari and positioning is expensive when used
                  in scale. https://github.com/chmln/flatpickr/issues/1096
                */
                if (!self.isMobile && isSafari) {
                    positionCalendar();
                }
                triggerEvent("onReady");
            }
            function bindToInstance(fn) {
                return fn.bind(self);
            }
            function setCalendarWidth() {
                var config = self.config;
                if (config.weekNumbers === false && config.showMonths === 1) {
                    return;
                }
                else if (config.noCalendar !== true) {
                    window.requestAnimationFrame(function () {
                        if (self.calendarContainer !== undefined) {
                            self.calendarContainer.style.visibility = "hidden";
                            self.calendarContainer.style.display = "block";
                        }
                        if (self.daysContainer !== undefined) {
                            var daysWidth = (self.days.offsetWidth + 1) * config.showMonths;
                            self.daysContainer.style.width = daysWidth + "px";
                            self.calendarContainer.style.width =
                                daysWidth +
                                    (self.weekWrapper !== undefined
                                        ? self.weekWrapper.offsetWidth
                                        : 0) +
                                    "px";
                            self.calendarContainer.style.removeProperty("visibility");
                            self.calendarContainer.style.removeProperty("display");
                        }
                    });
                }
            }
            /**
             * The handler for all events targeting the time inputs
             */
            function updateTime(e) {
                if (self.selectedDates.length === 0) {
                    var defaultDate = self.config.minDate !== undefined
                        ? new Date(self.config.minDate.getTime())
                        : new Date();
                    var _a = getDefaultHours(), hours = _a.hours, minutes = _a.minutes, seconds = _a.seconds;
                    defaultDate.setHours(hours, minutes, seconds, 0);
                    self.setDate(defaultDate, false);
                }
                if (e !== undefined && e.type !== "blur") {
                    timeWrapper(e);
                }
                var prevValue = self._input.value;
                setHoursFromInputs();
                updateValue();
                if (self._input.value !== prevValue) {
                    self._debouncedChange();
                }
            }
            function ampm2military(hour, amPM) {
                return (hour % 12) + 12 * int(amPM === self.l10n.amPM[1]);
            }
            function military2ampm(hour) {
                switch (hour % 24) {
                    case 0:
                    case 12:
                        return 12;
                    default:
                        return hour % 12;
                }
            }
            /**
             * Syncs the selected date object time with user's time input
             */
            function setHoursFromInputs() {
                if (self.hourElement === undefined || self.minuteElement === undefined)
                    return;
                var hours = (parseInt(self.hourElement.value.slice(-2), 10) || 0) % 24, minutes = (parseInt(self.minuteElement.value, 10) || 0) % 60, seconds = self.secondElement !== undefined
                    ? (parseInt(self.secondElement.value, 10) || 0) % 60
                    : 0;
                if (self.amPM !== undefined) {
                    hours = ampm2military(hours, self.amPM.textContent);
                }
                var limitMinHours = self.config.minTime !== undefined ||
                    (self.config.minDate &&
                        self.minDateHasTime &&
                        self.latestSelectedDateObj &&
                        compareDates(self.latestSelectedDateObj, self.config.minDate, true) ===
                            0);
                var limitMaxHours = self.config.maxTime !== undefined ||
                    (self.config.maxDate &&
                        self.maxDateHasTime &&
                        self.latestSelectedDateObj &&
                        compareDates(self.latestSelectedDateObj, self.config.maxDate, true) ===
                            0);
                if (limitMaxHours) {
                    var maxTime = self.config.maxTime !== undefined
                        ? self.config.maxTime
                        : self.config.maxDate;
                    hours = Math.min(hours, maxTime.getHours());
                    if (hours === maxTime.getHours())
                        minutes = Math.min(minutes, maxTime.getMinutes());
                    if (minutes === maxTime.getMinutes())
                        seconds = Math.min(seconds, maxTime.getSeconds());
                }
                if (limitMinHours) {
                    var minTime = self.config.minTime !== undefined
                        ? self.config.minTime
                        : self.config.minDate;
                    hours = Math.max(hours, minTime.getHours());
                    if (hours === minTime.getHours())
                        minutes = Math.max(minutes, minTime.getMinutes());
                    if (minutes === minTime.getMinutes())
                        seconds = Math.max(seconds, minTime.getSeconds());
                }
                setHours(hours, minutes, seconds);
            }
            /**
             * Syncs time input values with a date
             */
            function setHoursFromDate(dateObj) {
                var date = dateObj || self.latestSelectedDateObj;
                if (date) {
                    setHours(date.getHours(), date.getMinutes(), date.getSeconds());
                }
            }
            function getDefaultHours() {
                var hours = self.config.defaultHour;
                var minutes = self.config.defaultMinute;
                var seconds = self.config.defaultSeconds;
                if (self.config.minDate !== undefined) {
                    var minHr = self.config.minDate.getHours();
                    var minMinutes = self.config.minDate.getMinutes();
                    hours = Math.max(hours, minHr);
                    if (hours === minHr)
                        minutes = Math.max(minMinutes, minutes);
                    if (hours === minHr && minutes === minMinutes)
                        seconds = self.config.minDate.getSeconds();
                }
                if (self.config.maxDate !== undefined) {
                    var maxHr = self.config.maxDate.getHours();
                    var maxMinutes = self.config.maxDate.getMinutes();
                    hours = Math.min(hours, maxHr);
                    if (hours === maxHr)
                        minutes = Math.min(maxMinutes, minutes);
                    if (hours === maxHr && minutes === maxMinutes)
                        seconds = self.config.maxDate.getSeconds();
                }
                return { hours: hours, minutes: minutes, seconds: seconds };
            }
            /**
             * Sets the hours, minutes, and optionally seconds
             * of the latest selected date object and the
             * corresponding time inputs
             * @param {Number} hours the hour. whether its military
             *                 or am-pm gets inferred from config
             * @param {Number} minutes the minutes
             * @param {Number} seconds the seconds (optional)
             */
            function setHours(hours, minutes, seconds) {
                if (self.latestSelectedDateObj !== undefined) {
                    self.latestSelectedDateObj.setHours(hours % 24, minutes, seconds || 0, 0);
                }
                if (!self.hourElement || !self.minuteElement || self.isMobile)
                    return;
                self.hourElement.value = pad(!self.config.time_24hr
                    ? ((12 + hours) % 12) + 12 * int(hours % 12 === 0)
                    : hours);
                self.minuteElement.value = pad(minutes);
                if (self.amPM !== undefined)
                    self.amPM.textContent = self.l10n.amPM[int(hours >= 12)];
                if (self.secondElement !== undefined)
                    self.secondElement.value = pad(seconds);
            }
            /**
             * Handles the year input and incrementing events
             * @param {Event} event the keyup or increment event
             */
            function onYearInput(event) {
                var eventTarget = getEventTarget(event);
                var year = parseInt(eventTarget.value) + (event.delta || 0);
                if (year / 1000 > 1 ||
                    (event.key === "Enter" && !/[^\d]/.test(year.toString()))) {
                    changeYear(year);
                }
            }
            /**
             * Essentially addEventListener + tracking
             * @param {Element} element the element to addEventListener to
             * @param {String} event the event name
             * @param {Function} handler the event handler
             */
            function bind(element, event, handler, options) {
                if (event instanceof Array)
                    return event.forEach(function (ev) { return bind(element, ev, handler, options); });
                if (element instanceof Array)
                    return element.forEach(function (el) { return bind(el, event, handler, options); });
                element.addEventListener(event, handler, options);
                self._handlers.push({
                    element: element,
                    event: event,
                    handler: handler,
                    options: options,
                });
            }
            function triggerChange() {
                triggerEvent("onChange");
            }
            /**
             * Adds all the necessary event listeners
             */
            function bindEvents() {
                if (self.config.wrap) {
                    ["open", "close", "toggle", "clear"].forEach(function (evt) {
                        Array.prototype.forEach.call(self.element.querySelectorAll("[data-" + evt + "]"), function (el) {
                            return bind(el, "click", self[evt]);
                        });
                    });
                }
                if (self.isMobile) {
                    setupMobile();
                    return;
                }
                var debouncedResize = debounce(onResize, 50);
                self._debouncedChange = debounce(triggerChange, DEBOUNCED_CHANGE_MS);
                if (self.daysContainer && !/iPhone|iPad|iPod/i.test(navigator.userAgent))
                    bind(self.daysContainer, "mouseover", function (e) {
                        if (self.config.mode === "range")
                            onMouseOver(getEventTarget(e));
                    });
                bind(window.document.body, "keydown", onKeyDown);
                if (!self.config.inline && !self.config.static)
                    bind(window, "resize", debouncedResize);
                if (window.ontouchstart !== undefined)
                    bind(window.document, "touchstart", documentClick);
                else
                    bind(window.document, "click", documentClick);
                bind(window.document, "focus", documentClick, { capture: true });
                if (self.config.clickOpens === true) {
                    bind(self._input, "focus", self.open);
                    bind(self._input, "click", self.open);
                }
                if (self.daysContainer !== undefined) {
                    bind(self.monthNav, "click", onMonthNavClick);
                    bind(self.monthNav, ["keyup", "increment"], onYearInput);
                    bind(self.daysContainer, "click", selectDate);
                }
                if (self.timeContainer !== undefined &&
                    self.minuteElement !== undefined &&
                    self.hourElement !== undefined) {
                    var selText = function (e) {
                        return getEventTarget(e).select();
                    };
                    bind(self.timeContainer, ["increment"], updateTime);
                    bind(self.timeContainer, "blur", updateTime, { capture: true });
                    bind(self.timeContainer, "click", timeIncrement);
                    bind([self.hourElement, self.minuteElement], ["focus", "click"], selText);
                    if (self.secondElement !== undefined)
                        bind(self.secondElement, "focus", function () { return self.secondElement && self.secondElement.select(); });
                    if (self.amPM !== undefined) {
                        bind(self.amPM, "click", function (e) {
                            updateTime(e);
                            triggerChange();
                        });
                    }
                }
                if (self.config.allowInput)
                    bind(self._input, "blur", onBlur);
            }
            /**
             * Set the calendar view to a particular date.
             * @param {Date} jumpDate the date to set the view to
             * @param {boolean} triggerChange if change events should be triggered
             */
            function jumpToDate(jumpDate, triggerChange) {
                var jumpTo = jumpDate !== undefined
                    ? self.parseDate(jumpDate)
                    : self.latestSelectedDateObj ||
                        (self.config.minDate && self.config.minDate > self.now
                            ? self.config.minDate
                            : self.config.maxDate && self.config.maxDate < self.now
                                ? self.config.maxDate
                                : self.now);
                var oldYear = self.currentYear;
                var oldMonth = self.currentMonth;
                try {
                    if (jumpTo !== undefined) {
                        self.currentYear = jumpTo.getFullYear();
                        self.currentMonth = jumpTo.getMonth();
                    }
                }
                catch (e) {
                    /* istanbul ignore next */
                    e.message = "Invalid date supplied: " + jumpTo;
                    self.config.errorHandler(e);
                }
                if (triggerChange && self.currentYear !== oldYear) {
                    triggerEvent("onYearChange");
                    buildMonthSwitch();
                }
                if (triggerChange &&
                    (self.currentYear !== oldYear || self.currentMonth !== oldMonth)) {
                    triggerEvent("onMonthChange");
                }
                self.redraw();
            }
            /**
             * The up/down arrow handler for time inputs
             * @param {Event} e the click event
             */
            function timeIncrement(e) {
                var eventTarget = getEventTarget(e);
                if (~eventTarget.className.indexOf("arrow"))
                    incrementNumInput(e, eventTarget.classList.contains("arrowUp") ? 1 : -1);
            }
            /**
             * Increments/decrements the value of input associ-
             * ated with the up/down arrow by dispatching an
             * "increment" event on the input.
             *
             * @param {Event} e the click event
             * @param {Number} delta the diff (usually 1 or -1)
             * @param {Element} inputElem the input element
             */
            function incrementNumInput(e, delta, inputElem) {
                var target = e && getEventTarget(e);
                var input = inputElem ||
                    (target && target.parentNode && target.parentNode.firstChild);
                var event = createEvent("increment");
                event.delta = delta;
                input && input.dispatchEvent(event);
            }
            function build() {
                var fragment = window.document.createDocumentFragment();
                self.calendarContainer = createElement("div", "flatpickr-calendar");
                self.calendarContainer.tabIndex = -1;
                if (!self.config.noCalendar) {
                    fragment.appendChild(buildMonthNav());
                    self.innerContainer = createElement("div", "flatpickr-innerContainer");
                    if (self.config.weekNumbers) {
                        var _a = buildWeeks(), weekWrapper = _a.weekWrapper, weekNumbers = _a.weekNumbers;
                        self.innerContainer.appendChild(weekWrapper);
                        self.weekNumbers = weekNumbers;
                        self.weekWrapper = weekWrapper;
                    }
                    self.rContainer = createElement("div", "flatpickr-rContainer");
                    self.rContainer.appendChild(buildWeekdays());
                    if (!self.daysContainer) {
                        self.daysContainer = createElement("div", "flatpickr-days");
                        self.daysContainer.tabIndex = -1;
                    }
                    buildDays();
                    self.rContainer.appendChild(self.daysContainer);
                    self.innerContainer.appendChild(self.rContainer);
                    fragment.appendChild(self.innerContainer);
                }
                if (self.config.enableTime) {
                    fragment.appendChild(buildTime());
                }
                toggleClass(self.calendarContainer, "rangeMode", self.config.mode === "range");
                toggleClass(self.calendarContainer, "animate", self.config.animate === true);
                toggleClass(self.calendarContainer, "multiMonth", self.config.showMonths > 1);
                self.calendarContainer.appendChild(fragment);
                var customAppend = self.config.appendTo !== undefined &&
                    self.config.appendTo.nodeType !== undefined;
                if (self.config.inline || self.config.static) {
                    self.calendarContainer.classList.add(self.config.inline ? "inline" : "static");
                    if (self.config.inline) {
                        if (!customAppend && self.element.parentNode)
                            self.element.parentNode.insertBefore(self.calendarContainer, self._input.nextSibling);
                        else if (self.config.appendTo !== undefined)
                            self.config.appendTo.appendChild(self.calendarContainer);
                    }
                    if (self.config.static) {
                        var wrapper = createElement("div", "flatpickr-wrapper");
                        if (self.element.parentNode)
                            self.element.parentNode.insertBefore(wrapper, self.element);
                        wrapper.appendChild(self.element);
                        if (self.altInput)
                            wrapper.appendChild(self.altInput);
                        wrapper.appendChild(self.calendarContainer);
                    }
                }
                if (!self.config.static && !self.config.inline)
                    (self.config.appendTo !== undefined
                        ? self.config.appendTo
                        : window.document.body).appendChild(self.calendarContainer);
            }
            function createDay(className, date, dayNumber, i) {
                var dateIsEnabled = isEnabled(date, true), dayElement = createElement("span", "flatpickr-day " + className, date.getDate().toString());
                dayElement.dateObj = date;
                dayElement.$i = i;
                dayElement.setAttribute("aria-label", self.formatDate(date, self.config.ariaDateFormat));
                if (className.indexOf("hidden") === -1 &&
                    compareDates(date, self.now) === 0) {
                    self.todayDateElem = dayElement;
                    dayElement.classList.add("today");
                    dayElement.setAttribute("aria-current", "date");
                }
                if (dateIsEnabled) {
                    dayElement.tabIndex = -1;
                    if (isDateSelected(date)) {
                        dayElement.classList.add("selected");
                        self.selectedDateElem = dayElement;
                        if (self.config.mode === "range") {
                            toggleClass(dayElement, "startRange", self.selectedDates[0] &&
                                compareDates(date, self.selectedDates[0], true) === 0);
                            toggleClass(dayElement, "endRange", self.selectedDates[1] &&
                                compareDates(date, self.selectedDates[1], true) === 0);
                            if (className === "nextMonthDay")
                                dayElement.classList.add("inRange");
                        }
                    }
                }
                else {
                    dayElement.classList.add("flatpickr-disabled");
                }
                if (self.config.mode === "range") {
                    if (isDateInRange(date) && !isDateSelected(date))
                        dayElement.classList.add("inRange");
                }
                if (self.weekNumbers &&
                    self.config.showMonths === 1 &&
                    className !== "prevMonthDay" &&
                    dayNumber % 7 === 1) {
                    self.weekNumbers.insertAdjacentHTML("beforeend", "<span class='flatpickr-day'>" + self.config.getWeek(date) + "</span>");
                }
                triggerEvent("onDayCreate", dayElement);
                return dayElement;
            }
            function focusOnDayElem(targetNode) {
                targetNode.focus();
                if (self.config.mode === "range")
                    onMouseOver(targetNode);
            }
            function getFirstAvailableDay(delta) {
                var startMonth = delta > 0 ? 0 : self.config.showMonths - 1;
                var endMonth = delta > 0 ? self.config.showMonths : -1;
                for (var m = startMonth; m != endMonth; m += delta) {
                    var month = self.daysContainer.children[m];
                    var startIndex = delta > 0 ? 0 : month.children.length - 1;
                    var endIndex = delta > 0 ? month.children.length : -1;
                    for (var i = startIndex; i != endIndex; i += delta) {
                        var c = month.children[i];
                        if (c.className.indexOf("hidden") === -1 && isEnabled(c.dateObj))
                            return c;
                    }
                }
                return undefined;
            }
            function getNextAvailableDay(current, delta) {
                var givenMonth = current.className.indexOf("Month") === -1
                    ? current.dateObj.getMonth()
                    : self.currentMonth;
                var endMonth = delta > 0 ? self.config.showMonths : -1;
                var loopDelta = delta > 0 ? 1 : -1;
                for (var m = givenMonth - self.currentMonth; m != endMonth; m += loopDelta) {
                    var month = self.daysContainer.children[m];
                    var startIndex = givenMonth - self.currentMonth === m
                        ? current.$i + delta
                        : delta < 0
                            ? month.children.length - 1
                            : 0;
                    var numMonthDays = month.children.length;
                    for (var i = startIndex; i >= 0 && i < numMonthDays && i != (delta > 0 ? numMonthDays : -1); i += loopDelta) {
                        var c = month.children[i];
                        if (c.className.indexOf("hidden") === -1 &&
                            isEnabled(c.dateObj) &&
                            Math.abs(current.$i - i) >= Math.abs(delta))
                            return focusOnDayElem(c);
                    }
                }
                self.changeMonth(loopDelta);
                focusOnDay(getFirstAvailableDay(loopDelta), 0);
                return undefined;
            }
            function focusOnDay(current, offset) {
                var dayFocused = isInView(document.activeElement || document.body);
                var startElem = current !== undefined
                    ? current
                    : dayFocused
                        ? document.activeElement
                        : self.selectedDateElem !== undefined && isInView(self.selectedDateElem)
                            ? self.selectedDateElem
                            : self.todayDateElem !== undefined && isInView(self.todayDateElem)
                                ? self.todayDateElem
                                : getFirstAvailableDay(offset > 0 ? 1 : -1);
                if (startElem === undefined) {
                    self._input.focus();
                }
                else if (!dayFocused) {
                    focusOnDayElem(startElem);
                }
                else {
                    getNextAvailableDay(startElem, offset);
                }
            }
            function buildMonthDays(year, month) {
                var firstOfMonth = (new Date(year, month, 1).getDay() - self.l10n.firstDayOfWeek + 7) % 7;
                var prevMonthDays = self.utils.getDaysInMonth((month - 1 + 12) % 12, year);
                var daysInMonth = self.utils.getDaysInMonth(month, year), days = window.document.createDocumentFragment(), isMultiMonth = self.config.showMonths > 1, prevMonthDayClass = isMultiMonth ? "prevMonthDay hidden" : "prevMonthDay", nextMonthDayClass = isMultiMonth ? "nextMonthDay hidden" : "nextMonthDay";
                var dayNumber = prevMonthDays + 1 - firstOfMonth, dayIndex = 0;
                // prepend days from the ending of previous month
                for (; dayNumber <= prevMonthDays; dayNumber++, dayIndex++) {
                    days.appendChild(createDay(prevMonthDayClass, new Date(year, month - 1, dayNumber), dayNumber, dayIndex));
                }
                // Start at 1 since there is no 0th day
                for (dayNumber = 1; dayNumber <= daysInMonth; dayNumber++, dayIndex++) {
                    days.appendChild(createDay("", new Date(year, month, dayNumber), dayNumber, dayIndex));
                }
                // append days from the next month
                for (var dayNum = daysInMonth + 1; dayNum <= 42 - firstOfMonth &&
                    (self.config.showMonths === 1 || dayIndex % 7 !== 0); dayNum++, dayIndex++) {
                    days.appendChild(createDay(nextMonthDayClass, new Date(year, month + 1, dayNum % daysInMonth), dayNum, dayIndex));
                }
                //updateNavigationCurrentMonth();
                var dayContainer = createElement("div", "dayContainer");
                dayContainer.appendChild(days);
                return dayContainer;
            }
            function buildDays() {
                if (self.daysContainer === undefined) {
                    return;
                }
                clearNode(self.daysContainer);
                // TODO: week numbers for each month
                if (self.weekNumbers)
                    clearNode(self.weekNumbers);
                var frag = document.createDocumentFragment();
                for (var i = 0; i < self.config.showMonths; i++) {
                    var d = new Date(self.currentYear, self.currentMonth, 1);
                    d.setMonth(self.currentMonth + i);
                    frag.appendChild(buildMonthDays(d.getFullYear(), d.getMonth()));
                }
                self.daysContainer.appendChild(frag);
                self.days = self.daysContainer.firstChild;
                if (self.config.mode === "range" && self.selectedDates.length === 1) {
                    onMouseOver();
                }
            }
            function buildMonthSwitch() {
                if (self.config.showMonths > 1 ||
                    self.config.monthSelectorType !== "dropdown")
                    return;
                var shouldBuildMonth = function (month) {
                    if (self.config.minDate !== undefined &&
                        self.currentYear === self.config.minDate.getFullYear() &&
                        month < self.config.minDate.getMonth()) {
                        return false;
                    }
                    return !(self.config.maxDate !== undefined &&
                        self.currentYear === self.config.maxDate.getFullYear() &&
                        month > self.config.maxDate.getMonth());
                };
                self.monthsDropdownContainer.tabIndex = -1;
                self.monthsDropdownContainer.innerHTML = "";
                for (var i = 0; i < 12; i++) {
                    if (!shouldBuildMonth(i))
                        continue;
                    var month = createElement("option", "flatpickr-monthDropdown-month");
                    month.value = new Date(self.currentYear, i).getMonth().toString();
                    month.textContent = monthToStr(i, self.config.shorthandCurrentMonth, self.l10n);
                    month.tabIndex = -1;
                    if (self.currentMonth === i) {
                        month.selected = true;
                    }
                    self.monthsDropdownContainer.appendChild(month);
                }
            }
            function buildMonth() {
                var container = createElement("div", "flatpickr-month");
                var monthNavFragment = window.document.createDocumentFragment();
                var monthElement;
                if (self.config.showMonths > 1 ||
                    self.config.monthSelectorType === "static") {
                    monthElement = createElement("span", "cur-month");
                }
                else {
                    self.monthsDropdownContainer = createElement("select", "flatpickr-monthDropdown-months");
                    self.monthsDropdownContainer.setAttribute("aria-label", self.l10n.monthAriaLabel);
                    bind(self.monthsDropdownContainer, "change", function (e) {
                        var target = getEventTarget(e);
                        var selectedMonth = parseInt(target.value, 10);
                        self.changeMonth(selectedMonth - self.currentMonth);
                        triggerEvent("onMonthChange");
                    });
                    buildMonthSwitch();
                    monthElement = self.monthsDropdownContainer;
                }
                var yearInput = createNumberInput("cur-year", { tabindex: "-1" });
                var yearElement = yearInput.getElementsByTagName("input")[0];
                yearElement.setAttribute("aria-label", self.l10n.yearAriaLabel);
                if (self.config.minDate) {
                    yearElement.setAttribute("min", self.config.minDate.getFullYear().toString());
                }
                if (self.config.maxDate) {
                    yearElement.setAttribute("max", self.config.maxDate.getFullYear().toString());
                    yearElement.disabled =
                        !!self.config.minDate &&
                            self.config.minDate.getFullYear() === self.config.maxDate.getFullYear();
                }
                var currentMonth = createElement("div", "flatpickr-current-month");
                currentMonth.appendChild(monthElement);
                currentMonth.appendChild(yearInput);
                monthNavFragment.appendChild(currentMonth);
                container.appendChild(monthNavFragment);
                return {
                    container: container,
                    yearElement: yearElement,
                    monthElement: monthElement,
                };
            }
            function buildMonths() {
                clearNode(self.monthNav);
                self.monthNav.appendChild(self.prevMonthNav);
                if (self.config.showMonths) {
                    self.yearElements = [];
                    self.monthElements = [];
                }
                for (var m = self.config.showMonths; m--;) {
                    var month = buildMonth();
                    self.yearElements.push(month.yearElement);
                    self.monthElements.push(month.monthElement);
                    self.monthNav.appendChild(month.container);
                }
                self.monthNav.appendChild(self.nextMonthNav);
            }
            function buildMonthNav() {
                self.monthNav = createElement("div", "flatpickr-months");
                self.yearElements = [];
                self.monthElements = [];
                self.prevMonthNav = createElement("span", "flatpickr-prev-month");
                self.prevMonthNav.innerHTML = self.config.prevArrow;
                self.nextMonthNav = createElement("span", "flatpickr-next-month");
                self.nextMonthNav.innerHTML = self.config.nextArrow;
                buildMonths();
                Object.defineProperty(self, "_hidePrevMonthArrow", {
                    get: function () { return self.__hidePrevMonthArrow; },
                    set: function (bool) {
                        if (self.__hidePrevMonthArrow !== bool) {
                            toggleClass(self.prevMonthNav, "flatpickr-disabled", bool);
                            self.__hidePrevMonthArrow = bool;
                        }
                    },
                });
                Object.defineProperty(self, "_hideNextMonthArrow", {
                    get: function () { return self.__hideNextMonthArrow; },
                    set: function (bool) {
                        if (self.__hideNextMonthArrow !== bool) {
                            toggleClass(self.nextMonthNav, "flatpickr-disabled", bool);
                            self.__hideNextMonthArrow = bool;
                        }
                    },
                });
                self.currentYearElement = self.yearElements[0];
                updateNavigationCurrentMonth();
                return self.monthNav;
            }
            function buildTime() {
                self.calendarContainer.classList.add("hasTime");
                if (self.config.noCalendar)
                    self.calendarContainer.classList.add("noCalendar");
                self.timeContainer = createElement("div", "flatpickr-time");
                self.timeContainer.tabIndex = -1;
                var separator = createElement("span", "flatpickr-time-separator", ":");
                var hourInput = createNumberInput("flatpickr-hour", {
                    "aria-label": self.l10n.hourAriaLabel,
                });
                self.hourElement = hourInput.getElementsByTagName("input")[0];
                var minuteInput = createNumberInput("flatpickr-minute", {
                    "aria-label": self.l10n.minuteAriaLabel,
                });
                self.minuteElement = minuteInput.getElementsByTagName("input")[0];
                self.hourElement.tabIndex = self.minuteElement.tabIndex = -1;
                self.hourElement.value = pad(self.latestSelectedDateObj
                    ? self.latestSelectedDateObj.getHours()
                    : self.config.time_24hr
                        ? self.config.defaultHour
                        : military2ampm(self.config.defaultHour));
                self.minuteElement.value = pad(self.latestSelectedDateObj
                    ? self.latestSelectedDateObj.getMinutes()
                    : self.config.defaultMinute);
                self.hourElement.setAttribute("step", self.config.hourIncrement.toString());
                self.minuteElement.setAttribute("step", self.config.minuteIncrement.toString());
                self.hourElement.setAttribute("min", self.config.time_24hr ? "0" : "1");
                self.hourElement.setAttribute("max", self.config.time_24hr ? "23" : "12");
                self.minuteElement.setAttribute("min", "0");
                self.minuteElement.setAttribute("max", "59");
                self.timeContainer.appendChild(hourInput);
                self.timeContainer.appendChild(separator);
                self.timeContainer.appendChild(minuteInput);
                if (self.config.time_24hr)
                    self.timeContainer.classList.add("time24hr");
                if (self.config.enableSeconds) {
                    self.timeContainer.classList.add("hasSeconds");
                    var secondInput = createNumberInput("flatpickr-second");
                    self.secondElement = secondInput.getElementsByTagName("input")[0];
                    self.secondElement.value = pad(self.latestSelectedDateObj
                        ? self.latestSelectedDateObj.getSeconds()
                        : self.config.defaultSeconds);
                    self.secondElement.setAttribute("step", self.minuteElement.getAttribute("step"));
                    self.secondElement.setAttribute("min", "0");
                    self.secondElement.setAttribute("max", "59");
                    self.timeContainer.appendChild(createElement("span", "flatpickr-time-separator", ":"));
                    self.timeContainer.appendChild(secondInput);
                }
                if (!self.config.time_24hr) {
                    // add self.amPM if appropriate
                    self.amPM = createElement("span", "flatpickr-am-pm", self.l10n.amPM[int((self.latestSelectedDateObj
                        ? self.hourElement.value
                        : self.config.defaultHour) > 11)]);
                    self.amPM.title = self.l10n.toggleTitle;
                    self.amPM.tabIndex = -1;
                    self.timeContainer.appendChild(self.amPM);
                }
                return self.timeContainer;
            }
            function buildWeekdays() {
                if (!self.weekdayContainer)
                    self.weekdayContainer = createElement("div", "flatpickr-weekdays");
                else
                    clearNode(self.weekdayContainer);
                for (var i = self.config.showMonths; i--;) {
                    var container = createElement("div", "flatpickr-weekdaycontainer");
                    self.weekdayContainer.appendChild(container);
                }
                updateWeekdays();
                return self.weekdayContainer;
            }
            function updateWeekdays() {
                if (!self.weekdayContainer) {
                    return;
                }
                var firstDayOfWeek = self.l10n.firstDayOfWeek;
                var weekdays = __spreadArrays(self.l10n.weekdays.shorthand);
                if (firstDayOfWeek > 0 && firstDayOfWeek < weekdays.length) {
                    weekdays = __spreadArrays(weekdays.splice(firstDayOfWeek, weekdays.length), weekdays.splice(0, firstDayOfWeek));
                }
                for (var i = self.config.showMonths; i--;) {
                    self.weekdayContainer.children[i].innerHTML = "\n      <span class='flatpickr-weekday'>\n        " + weekdays.join("</span><span class='flatpickr-weekday'>") + "\n      </span>\n      ";
                }
            }
            /* istanbul ignore next */
            function buildWeeks() {
                self.calendarContainer.classList.add("hasWeeks");
                var weekWrapper = createElement("div", "flatpickr-weekwrapper");
                weekWrapper.appendChild(createElement("span", "flatpickr-weekday", self.l10n.weekAbbreviation));
                var weekNumbers = createElement("div", "flatpickr-weeks");
                weekWrapper.appendChild(weekNumbers);
                return {
                    weekWrapper: weekWrapper,
                    weekNumbers: weekNumbers,
                };
            }
            function changeMonth(value, isOffset) {
                if (isOffset === void 0) { isOffset = true; }
                var delta = isOffset ? value : value - self.currentMonth;
                if ((delta < 0 && self._hidePrevMonthArrow === true) ||
                    (delta > 0 && self._hideNextMonthArrow === true))
                    return;
                self.currentMonth += delta;
                if (self.currentMonth < 0 || self.currentMonth > 11) {
                    self.currentYear += self.currentMonth > 11 ? 1 : -1;
                    self.currentMonth = (self.currentMonth + 12) % 12;
                    triggerEvent("onYearChange");
                    buildMonthSwitch();
                }
                buildDays();
                triggerEvent("onMonthChange");
                updateNavigationCurrentMonth();
            }
            function clear(triggerChangeEvent, toInitial) {
                if (triggerChangeEvent === void 0) { triggerChangeEvent = true; }
                if (toInitial === void 0) { toInitial = true; }
                self.input.value = "";
                if (self.altInput !== undefined)
                    self.altInput.value = "";
                if (self.mobileInput !== undefined)
                    self.mobileInput.value = "";
                self.selectedDates = [];
                self.latestSelectedDateObj = undefined;
                if (toInitial === true) {
                    self.currentYear = self._initialDate.getFullYear();
                    self.currentMonth = self._initialDate.getMonth();
                }
                if (self.config.enableTime === true) {
                    var _a = getDefaultHours(), hours = _a.hours, minutes = _a.minutes, seconds = _a.seconds;
                    setHours(hours, minutes, seconds);
                }
                self.redraw();
                if (triggerChangeEvent)
                    // triggerChangeEvent is true (default) or an Event
                    triggerEvent("onChange");
            }
            function close() {
                self.isOpen = false;
                if (!self.isMobile) {
                    if (self.calendarContainer !== undefined) {
                        self.calendarContainer.classList.remove("open");
                    }
                    if (self._input !== undefined) {
                        self._input.classList.remove("active");
                    }
                }
                triggerEvent("onClose");
            }
            function destroy() {
                if (self.config !== undefined)
                    triggerEvent("onDestroy");
                for (var i = self._handlers.length; i--;) {
                    var h = self._handlers[i];
                    h.element.removeEventListener(h.event, h.handler, h.options);
                }
                self._handlers = [];
                if (self.mobileInput) {
                    if (self.mobileInput.parentNode)
                        self.mobileInput.parentNode.removeChild(self.mobileInput);
                    self.mobileInput = undefined;
                }
                else if (self.calendarContainer && self.calendarContainer.parentNode) {
                    if (self.config.static && self.calendarContainer.parentNode) {
                        var wrapper = self.calendarContainer.parentNode;
                        wrapper.lastChild && wrapper.removeChild(wrapper.lastChild);
                        if (wrapper.parentNode) {
                            while (wrapper.firstChild)
                                wrapper.parentNode.insertBefore(wrapper.firstChild, wrapper);
                            wrapper.parentNode.removeChild(wrapper);
                        }
                    }
                    else
                        self.calendarContainer.parentNode.removeChild(self.calendarContainer);
                }
                if (self.altInput) {
                    self.input.type = "text";
                    if (self.altInput.parentNode)
                        self.altInput.parentNode.removeChild(self.altInput);
                    delete self.altInput;
                }
                if (self.input) {
                    self.input.type = self.input._type;
                    self.input.classList.remove("flatpickr-input");
                    self.input.removeAttribute("readonly");
                }
                [
                    "_showTimeInput",
                    "latestSelectedDateObj",
                    "_hideNextMonthArrow",
                    "_hidePrevMonthArrow",
                    "__hideNextMonthArrow",
                    "__hidePrevMonthArrow",
                    "isMobile",
                    "isOpen",
                    "selectedDateElem",
                    "minDateHasTime",
                    "maxDateHasTime",
                    "days",
                    "daysContainer",
                    "_input",
                    "_positionElement",
                    "innerContainer",
                    "rContainer",
                    "monthNav",
                    "todayDateElem",
                    "calendarContainer",
                    "weekdayContainer",
                    "prevMonthNav",
                    "nextMonthNav",
                    "monthsDropdownContainer",
                    "currentMonthElement",
                    "currentYearElement",
                    "navigationCurrentMonth",
                    "selectedDateElem",
                    "config",
                ].forEach(function (k) {
                    try {
                        delete self[k];
                    }
                    catch (_) { }
                });
            }
            function isCalendarElem(elem) {
                if (self.config.appendTo && self.config.appendTo.contains(elem))
                    return true;
                return self.calendarContainer.contains(elem);
            }
            function documentClick(e) {
                if (self.isOpen && !self.config.inline) {
                    var eventTarget_1 = getEventTarget(e);
                    var isCalendarElement = isCalendarElem(eventTarget_1);
                    var isInput = eventTarget_1 === self.input ||
                        eventTarget_1 === self.altInput ||
                        self.element.contains(eventTarget_1) ||
                        // web components
                        // e.path is not present in all browsers. circumventing typechecks
                        (e.path &&
                            e.path.indexOf &&
                            (~e.path.indexOf(self.input) ||
                                ~e.path.indexOf(self.altInput)));
                    var lostFocus = e.type === "blur"
                        ? isInput &&
                            e.relatedTarget &&
                            !isCalendarElem(e.relatedTarget)
                        : !isInput &&
                            !isCalendarElement &&
                            !isCalendarElem(e.relatedTarget);
                    var isIgnored = !self.config.ignoredFocusElements.some(function (elem) {
                        return elem.contains(eventTarget_1);
                    });
                    if (lostFocus && isIgnored) {
                        if (self.timeContainer !== undefined &&
                            self.minuteElement !== undefined &&
                            self.hourElement !== undefined &&
                            self.input.value !== "" &&
                            self.input.value !== undefined) {
                            updateTime();
                        }
                        self.close();
                        if (self.config &&
                            self.config.mode === "range" &&
                            self.selectedDates.length === 1) {
                            self.clear(false);
                            self.redraw();
                        }
                    }
                }
            }
            function changeYear(newYear) {
                if (!newYear ||
                    (self.config.minDate && newYear < self.config.minDate.getFullYear()) ||
                    (self.config.maxDate && newYear > self.config.maxDate.getFullYear()))
                    return;
                var newYearNum = newYear, isNewYear = self.currentYear !== newYearNum;
                self.currentYear = newYearNum || self.currentYear;
                if (self.config.maxDate &&
                    self.currentYear === self.config.maxDate.getFullYear()) {
                    self.currentMonth = Math.min(self.config.maxDate.getMonth(), self.currentMonth);
                }
                else if (self.config.minDate &&
                    self.currentYear === self.config.minDate.getFullYear()) {
                    self.currentMonth = Math.max(self.config.minDate.getMonth(), self.currentMonth);
                }
                if (isNewYear) {
                    self.redraw();
                    triggerEvent("onYearChange");
                    buildMonthSwitch();
                }
            }
            function isEnabled(date, timeless) {
                if (timeless === void 0) { timeless = true; }
                var dateToCheck = self.parseDate(date, undefined, timeless); // timeless
                if ((self.config.minDate &&
                    dateToCheck &&
                    compareDates(dateToCheck, self.config.minDate, timeless !== undefined ? timeless : !self.minDateHasTime) < 0) ||
                    (self.config.maxDate &&
                        dateToCheck &&
                        compareDates(dateToCheck, self.config.maxDate, timeless !== undefined ? timeless : !self.maxDateHasTime) > 0))
                    return false;
                if (self.config.enable.length === 0 && self.config.disable.length === 0)
                    return true;
                if (dateToCheck === undefined)
                    return false;
                var bool = self.config.enable.length > 0, array = bool ? self.config.enable : self.config.disable;
                for (var i = 0, d = void 0; i < array.length; i++) {
                    d = array[i];
                    if (typeof d === "function" &&
                        d(dateToCheck) // disabled by function
                    )
                        return bool;
                    else if (d instanceof Date &&
                        dateToCheck !== undefined &&
                        d.getTime() === dateToCheck.getTime())
                        // disabled by date
                        return bool;
                    else if (typeof d === "string" && dateToCheck !== undefined) {
                        // disabled by date string
                        var parsed = self.parseDate(d, undefined, true);
                        return parsed && parsed.getTime() === dateToCheck.getTime()
                            ? bool
                            : !bool;
                    }
                    else if (
                    // disabled by range
                    typeof d === "object" &&
                        dateToCheck !== undefined &&
                        d.from &&
                        d.to &&
                        dateToCheck.getTime() >= d.from.getTime() &&
                        dateToCheck.getTime() <= d.to.getTime())
                        return bool;
                }
                return !bool;
            }
            function isInView(elem) {
                if (self.daysContainer !== undefined)
                    return (elem.className.indexOf("hidden") === -1 &&
                        elem.className.indexOf("flatpickr-disabled") === -1 &&
                        self.daysContainer.contains(elem));
                return false;
            }
            function onBlur(e) {
                var isInput = e.target === self._input;
                if (isInput &&
                    !(e.relatedTarget && isCalendarElem(e.relatedTarget))) {
                    self.setDate(self._input.value, true, e.target === self.altInput
                        ? self.config.altFormat
                        : self.config.dateFormat);
                }
            }
            function onKeyDown(e) {
                // e.key                      e.keyCode
                // "Backspace"                        8
                // "Tab"                              9
                // "Enter"                           13
                // "Escape"     (IE "Esc")           27
                // "ArrowLeft"  (IE "Left")          37
                // "ArrowUp"    (IE "Up")            38
                // "ArrowRight" (IE "Right")         39
                // "ArrowDown"  (IE "Down")          40
                // "Delete"     (IE "Del")           46
                var eventTarget = getEventTarget(e);
                var isInput = self.config.wrap
                    ? element.contains(eventTarget)
                    : eventTarget === self._input;
                var allowInput = self.config.allowInput;
                var allowKeydown = self.isOpen && (!allowInput || !isInput);
                var allowInlineKeydown = self.config.inline && isInput && !allowInput;
                if (e.keyCode === 13 && isInput) {
                    if (allowInput) {
                        self.setDate(self._input.value, true, eventTarget === self.altInput
                            ? self.config.altFormat
                            : self.config.dateFormat);
                        return eventTarget.blur();
                    }
                    else {
                        self.open();
                    }
                }
                else if (isCalendarElem(eventTarget) ||
                    allowKeydown ||
                    allowInlineKeydown) {
                    var isTimeObj = !!self.timeContainer &&
                        self.timeContainer.contains(eventTarget);
                    switch (e.keyCode) {
                        case 13:
                            if (isTimeObj) {
                                e.preventDefault();
                                updateTime();
                                focusAndClose();
                            }
                            else
                                selectDate(e);
                            break;
                        case 27: // escape
                            e.preventDefault();
                            focusAndClose();
                            break;
                        case 8:
                        case 46:
                            if (isInput && !self.config.allowInput) {
                                e.preventDefault();
                                self.clear();
                            }
                            break;
                        case 37:
                        case 39:
                            if (!isTimeObj && !isInput) {
                                e.preventDefault();
                                if (self.daysContainer !== undefined &&
                                    (allowInput === false ||
                                        (document.activeElement && isInView(document.activeElement)))) {
                                    var delta_1 = e.keyCode === 39 ? 1 : -1;
                                    if (!e.ctrlKey)
                                        focusOnDay(undefined, delta_1);
                                    else {
                                        e.stopPropagation();
                                        changeMonth(delta_1);
                                        focusOnDay(getFirstAvailableDay(1), 0);
                                    }
                                }
                            }
                            else if (self.hourElement)
                                self.hourElement.focus();
                            break;
                        case 38:
                        case 40:
                            e.preventDefault();
                            var delta = e.keyCode === 40 ? 1 : -1;
                            if ((self.daysContainer &&
                                eventTarget.$i !== undefined) ||
                                eventTarget === self.input ||
                                eventTarget === self.altInput) {
                                if (e.ctrlKey) {
                                    e.stopPropagation();
                                    changeYear(self.currentYear - delta);
                                    focusOnDay(getFirstAvailableDay(1), 0);
                                }
                                else if (!isTimeObj)
                                    focusOnDay(undefined, delta * 7);
                            }
                            else if (eventTarget === self.currentYearElement) {
                                changeYear(self.currentYear - delta);
                            }
                            else if (self.config.enableTime) {
                                if (!isTimeObj && self.hourElement)
                                    self.hourElement.focus();
                                updateTime(e);
                                self._debouncedChange();
                            }
                            break;
                        case 9:
                            if (isTimeObj) {
                                var elems = [
                                    self.hourElement,
                                    self.minuteElement,
                                    self.secondElement,
                                    self.amPM,
                                ]
                                    .concat(self.pluginElements)
                                    .filter(function (x) { return x; });
                                var i = elems.indexOf(eventTarget);
                                if (i !== -1) {
                                    var target = elems[i + (e.shiftKey ? -1 : 1)];
                                    e.preventDefault();
                                    (target || self._input).focus();
                                }
                            }
                            else if (!self.config.noCalendar &&
                                self.daysContainer &&
                                self.daysContainer.contains(eventTarget) &&
                                e.shiftKey) {
                                e.preventDefault();
                                self._input.focus();
                            }
                            break;
                    }
                }
                if (self.amPM !== undefined && eventTarget === self.amPM) {
                    switch (e.key) {
                        case self.l10n.amPM[0].charAt(0):
                        case self.l10n.amPM[0].charAt(0).toLowerCase():
                            self.amPM.textContent = self.l10n.amPM[0];
                            setHoursFromInputs();
                            updateValue();
                            break;
                        case self.l10n.amPM[1].charAt(0):
                        case self.l10n.amPM[1].charAt(0).toLowerCase():
                            self.amPM.textContent = self.l10n.amPM[1];
                            setHoursFromInputs();
                            updateValue();
                            break;
                    }
                }
                if (isInput || isCalendarElem(eventTarget)) {
                    triggerEvent("onKeyDown", e);
                }
            }
            function onMouseOver(elem) {
                if (self.selectedDates.length !== 1 ||
                    (elem &&
                        (!elem.classList.contains("flatpickr-day") ||
                            elem.classList.contains("flatpickr-disabled"))))
                    return;
                var hoverDate = elem
                    ? elem.dateObj.getTime()
                    : self.days.firstElementChild.dateObj.getTime(), initialDate = self.parseDate(self.selectedDates[0], undefined, true).getTime(), rangeStartDate = Math.min(hoverDate, self.selectedDates[0].getTime()), rangeEndDate = Math.max(hoverDate, self.selectedDates[0].getTime());
                var containsDisabled = false;
                var minRange = 0, maxRange = 0;
                for (var t = rangeStartDate; t < rangeEndDate; t += duration.DAY) {
                    if (!isEnabled(new Date(t), true)) {
                        containsDisabled =
                            containsDisabled || (t > rangeStartDate && t < rangeEndDate);
                        if (t < initialDate && (!minRange || t > minRange))
                            minRange = t;
                        else if (t > initialDate && (!maxRange || t < maxRange))
                            maxRange = t;
                    }
                }
                for (var m = 0; m < self.config.showMonths; m++) {
                    var month = self.daysContainer.children[m];
                    var _loop_1 = function (i, l) {
                        var dayElem = month.children[i], date = dayElem.dateObj;
                        var timestamp = date.getTime();
                        var outOfRange = (minRange > 0 && timestamp < minRange) ||
                            (maxRange > 0 && timestamp > maxRange);
                        if (outOfRange) {
                            dayElem.classList.add("notAllowed");
                            ["inRange", "startRange", "endRange"].forEach(function (c) {
                                dayElem.classList.remove(c);
                            });
                            return "continue";
                        }
                        else if (containsDisabled && !outOfRange)
                            return "continue";
                        ["startRange", "inRange", "endRange", "notAllowed"].forEach(function (c) {
                            dayElem.classList.remove(c);
                        });
                        if (elem !== undefined) {
                            elem.classList.add(hoverDate <= self.selectedDates[0].getTime()
                                ? "startRange"
                                : "endRange");
                            if (initialDate < hoverDate && timestamp === initialDate)
                                dayElem.classList.add("startRange");
                            else if (initialDate > hoverDate && timestamp === initialDate)
                                dayElem.classList.add("endRange");
                            if (timestamp >= minRange &&
                                (maxRange === 0 || timestamp <= maxRange) &&
                                isBetween(timestamp, initialDate, hoverDate))
                                dayElem.classList.add("inRange");
                        }
                    };
                    for (var i = 0, l = month.children.length; i < l; i++) {
                        _loop_1(i, l);
                    }
                }
            }
            function onResize() {
                if (self.isOpen && !self.config.static && !self.config.inline)
                    positionCalendar();
            }
            function open(e, positionElement) {
                if (positionElement === void 0) { positionElement = self._positionElement; }
                if (self.isMobile === true) {
                    if (e) {
                        e.preventDefault();
                        var eventTarget = getEventTarget(e);
                        eventTarget && eventTarget.blur();
                    }
                    if (self.mobileInput !== undefined) {
                        self.mobileInput.focus();
                        self.mobileInput.click();
                    }
                    triggerEvent("onOpen");
                    return;
                }
                if (self._input.disabled || self.config.inline)
                    return;
                var wasOpen = self.isOpen;
                self.isOpen = true;
                if (!wasOpen) {
                    self.calendarContainer.classList.add("open");
                    self._input.classList.add("active");
                    triggerEvent("onOpen");
                    positionCalendar(positionElement);
                }
                if (self.config.enableTime === true && self.config.noCalendar === true) {
                    if (self.config.allowInput === false &&
                        (e === undefined ||
                            !self.timeContainer.contains(e.relatedTarget))) {
                        setTimeout(function () { return self.hourElement.select(); }, 50);
                    }
                }
            }
            function minMaxDateSetter(type) {
                return function (date) {
                    var dateObj = (self.config["_" + type + "Date"] = self.parseDate(date, self.config.dateFormat));
                    var inverseDateObj = self.config["_" + (type === "min" ? "max" : "min") + "Date"];
                    if (dateObj !== undefined) {
                        self[type === "min" ? "minDateHasTime" : "maxDateHasTime"] =
                            dateObj.getHours() > 0 ||
                                dateObj.getMinutes() > 0 ||
                                dateObj.getSeconds() > 0;
                    }
                    if (self.selectedDates) {
                        self.selectedDates = self.selectedDates.filter(function (d) { return isEnabled(d); });
                        if (!self.selectedDates.length && type === "min")
                            setHoursFromDate(dateObj);
                        updateValue();
                    }
                    if (self.daysContainer) {
                        redraw();
                        if (dateObj !== undefined)
                            self.currentYearElement[type] = dateObj.getFullYear().toString();
                        else
                            self.currentYearElement.removeAttribute(type);
                        self.currentYearElement.disabled =
                            !!inverseDateObj &&
                                dateObj !== undefined &&
                                inverseDateObj.getFullYear() === dateObj.getFullYear();
                    }
                };
            }
            function parseConfig() {
                var boolOpts = [
                    "wrap",
                    "weekNumbers",
                    "allowInput",
                    "allowInvalidPreload",
                    "clickOpens",
                    "time_24hr",
                    "enableTime",
                    "noCalendar",
                    "altInput",
                    "shorthandCurrentMonth",
                    "inline",
                    "static",
                    "enableSeconds",
                    "disableMobile",
                ];
                var userConfig = __assign(__assign({}, JSON.parse(JSON.stringify(element.dataset || {}))), instanceConfig);
                var formats = {};
                self.config.parseDate = userConfig.parseDate;
                self.config.formatDate = userConfig.formatDate;
                Object.defineProperty(self.config, "enable", {
                    get: function () { return self.config._enable; },
                    set: function (dates) {
                        self.config._enable = parseDateRules(dates);
                    },
                });
                Object.defineProperty(self.config, "disable", {
                    get: function () { return self.config._disable; },
                    set: function (dates) {
                        self.config._disable = parseDateRules(dates);
                    },
                });
                var timeMode = userConfig.mode === "time";
                if (!userConfig.dateFormat && (userConfig.enableTime || timeMode)) {
                    var defaultDateFormat = flatpickr.defaultConfig.dateFormat || defaults.dateFormat;
                    formats.dateFormat =
                        userConfig.noCalendar || timeMode
                            ? "H:i" + (userConfig.enableSeconds ? ":S" : "")
                            : defaultDateFormat + " H:i" + (userConfig.enableSeconds ? ":S" : "");
                }
                if (userConfig.altInput &&
                    (userConfig.enableTime || timeMode) &&
                    !userConfig.altFormat) {
                    var defaultAltFormat = flatpickr.defaultConfig.altFormat || defaults.altFormat;
                    formats.altFormat =
                        userConfig.noCalendar || timeMode
                            ? "h:i" + (userConfig.enableSeconds ? ":S K" : " K")
                            : defaultAltFormat + (" h:i" + (userConfig.enableSeconds ? ":S" : "") + " K");
                }
                Object.defineProperty(self.config, "minDate", {
                    get: function () { return self.config._minDate; },
                    set: minMaxDateSetter("min"),
                });
                Object.defineProperty(self.config, "maxDate", {
                    get: function () { return self.config._maxDate; },
                    set: minMaxDateSetter("max"),
                });
                var minMaxTimeSetter = function (type) { return function (val) {
                    self.config[type === "min" ? "_minTime" : "_maxTime"] = self.parseDate(val, "H:i:S");
                }; };
                Object.defineProperty(self.config, "minTime", {
                    get: function () { return self.config._minTime; },
                    set: minMaxTimeSetter("min"),
                });
                Object.defineProperty(self.config, "maxTime", {
                    get: function () { return self.config._maxTime; },
                    set: minMaxTimeSetter("max"),
                });
                if (userConfig.mode === "time") {
                    self.config.noCalendar = true;
                    self.config.enableTime = true;
                }
                Object.assign(self.config, formats, userConfig);
                for (var i = 0; i < boolOpts.length; i++)
                    // https://github.com/microsoft/TypeScript/issues/31663
                    self.config[boolOpts[i]] =
                        self.config[boolOpts[i]] === true ||
                            self.config[boolOpts[i]] === "true";
                HOOKS.filter(function (hook) { return self.config[hook] !== undefined; }).forEach(function (hook) {
                    self.config[hook] = arrayify(self.config[hook] || []).map(bindToInstance);
                });
                self.isMobile =
                    !self.config.disableMobile &&
                        !self.config.inline &&
                        self.config.mode === "single" &&
                        !self.config.disable.length &&
                        !self.config.enable.length &&
                        !self.config.weekNumbers &&
                        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                for (var i = 0; i < self.config.plugins.length; i++) {
                    var pluginConf = self.config.plugins[i](self) || {};
                    for (var key in pluginConf) {
                        if (HOOKS.indexOf(key) > -1) {
                            self.config[key] = arrayify(pluginConf[key])
                                .map(bindToInstance)
                                .concat(self.config[key]);
                        }
                        else if (typeof userConfig[key] === "undefined")
                            self.config[key] = pluginConf[key];
                    }
                }
                if (!userConfig.altInputClass) {
                    self.config.altInputClass =
                        getInputElem().className + " " + self.config.altInputClass;
                }
                triggerEvent("onParseConfig");
            }
            function getInputElem() {
                return self.config.wrap
                    ? element.querySelector("[data-input]")
                    : element;
            }
            function setupLocale() {
                if (typeof self.config.locale !== "object" &&
                    typeof flatpickr.l10ns[self.config.locale] === "undefined")
                    self.config.errorHandler(new Error("flatpickr: invalid locale " + self.config.locale));
                self.l10n = __assign(__assign({}, flatpickr.l10ns.default), (typeof self.config.locale === "object"
                    ? self.config.locale
                    : self.config.locale !== "default"
                        ? flatpickr.l10ns[self.config.locale]
                        : undefined));
                tokenRegex.K = "(" + self.l10n.amPM[0] + "|" + self.l10n.amPM[1] + "|" + self.l10n.amPM[0].toLowerCase() + "|" + self.l10n.amPM[1].toLowerCase() + ")";
                var userConfig = __assign(__assign({}, instanceConfig), JSON.parse(JSON.stringify(element.dataset || {})));
                if (userConfig.time_24hr === undefined &&
                    flatpickr.defaultConfig.time_24hr === undefined) {
                    self.config.time_24hr = self.l10n.time_24hr;
                }
                self.formatDate = createDateFormatter(self);
                self.parseDate = createDateParser({ config: self.config, l10n: self.l10n });
            }
            function positionCalendar(customPositionElement) {
                if (self.calendarContainer === undefined)
                    return;
                triggerEvent("onPreCalendarPosition");
                var positionElement = customPositionElement || self._positionElement;
                var calendarHeight = Array.prototype.reduce.call(self.calendarContainer.children, (function (acc, child) { return acc + child.offsetHeight; }), 0), calendarWidth = self.calendarContainer.offsetWidth, configPos = self.config.position.split(" "), configPosVertical = configPos[0], configPosHorizontal = configPos.length > 1 ? configPos[1] : null, inputBounds = positionElement.getBoundingClientRect(), distanceFromBottom = window.innerHeight - inputBounds.bottom, showOnTop = configPosVertical === "above" ||
                    (configPosVertical !== "below" &&
                        distanceFromBottom < calendarHeight &&
                        inputBounds.top > calendarHeight);
                var top = window.pageYOffset +
                    inputBounds.top +
                    (!showOnTop ? positionElement.offsetHeight + 2 : -calendarHeight - 2);
                toggleClass(self.calendarContainer, "arrowTop", !showOnTop);
                toggleClass(self.calendarContainer, "arrowBottom", showOnTop);
                if (self.config.inline)
                    return;
                var left = window.pageXOffset + inputBounds.left;
                var isCenter = false;
                var isRight = false;
                if (configPosHorizontal === "center") {
                    left -= (calendarWidth - inputBounds.width) / 2;
                    isCenter = true;
                }
                else if (configPosHorizontal === "right") {
                    left -= calendarWidth - inputBounds.width;
                    isRight = true;
                }
                toggleClass(self.calendarContainer, "arrowLeft", !isCenter && !isRight);
                toggleClass(self.calendarContainer, "arrowCenter", isCenter);
                toggleClass(self.calendarContainer, "arrowRight", isRight);
                var right = window.document.body.offsetWidth -
                    (window.pageXOffset + inputBounds.right);
                var rightMost = left + calendarWidth > window.document.body.offsetWidth;
                var centerMost = right + calendarWidth > window.document.body.offsetWidth;
                toggleClass(self.calendarContainer, "rightMost", rightMost);
                if (self.config.static)
                    return;
                self.calendarContainer.style.top = top + "px";
                if (!rightMost) {
                    self.calendarContainer.style.left = left + "px";
                    self.calendarContainer.style.right = "auto";
                }
                else if (!centerMost) {
                    self.calendarContainer.style.left = "auto";
                    self.calendarContainer.style.right = right + "px";
                }
                else {
                    var doc = getDocumentStyleSheet();
                    // some testing environments don't have css support
                    if (doc === undefined)
                        return;
                    var bodyWidth = window.document.body.offsetWidth;
                    var centerLeft = Math.max(0, bodyWidth / 2 - calendarWidth / 2);
                    var centerBefore = ".flatpickr-calendar.centerMost:before";
                    var centerAfter = ".flatpickr-calendar.centerMost:after";
                    var centerIndex = doc.cssRules.length;
                    var centerStyle = "{left:" + inputBounds.left + "px;right:auto;}";
                    toggleClass(self.calendarContainer, "rightMost", false);
                    toggleClass(self.calendarContainer, "centerMost", true);
                    doc.insertRule(centerBefore + "," + centerAfter + centerStyle, centerIndex);
                    self.calendarContainer.style.left = centerLeft + "px";
                    self.calendarContainer.style.right = "auto";
                }
            }
            function getDocumentStyleSheet() {
                var editableSheet = null;
                for (var i = 0; i < document.styleSheets.length; i++) {
                    var sheet = document.styleSheets[i];
                    try {
                        sheet.cssRules;
                    }
                    catch (err) {
                        continue;
                    }
                    editableSheet = sheet;
                    break;
                }
                return editableSheet != null ? editableSheet : createStyleSheet();
            }
            function createStyleSheet() {
                var style = document.createElement("style");
                document.head.appendChild(style);
                return style.sheet;
            }
            function redraw() {
                if (self.config.noCalendar || self.isMobile)
                    return;
                buildMonthSwitch();
                updateNavigationCurrentMonth();
                buildDays();
            }
            function focusAndClose() {
                self._input.focus();
                if (window.navigator.userAgent.indexOf("MSIE") !== -1 ||
                    navigator.msMaxTouchPoints !== undefined) {
                    // hack - bugs in the way IE handles focus keeps the calendar open
                    setTimeout(self.close, 0);
                }
                else {
                    self.close();
                }
            }
            function selectDate(e) {
                e.preventDefault();
                e.stopPropagation();
                var isSelectable = function (day) {
                    return day.classList &&
                        day.classList.contains("flatpickr-day") &&
                        !day.classList.contains("flatpickr-disabled") &&
                        !day.classList.contains("notAllowed");
                };
                var t = findParent(getEventTarget(e), isSelectable);
                if (t === undefined)
                    return;
                var target = t;
                var selectedDate = (self.latestSelectedDateObj = new Date(target.dateObj.getTime()));
                var shouldChangeMonth = (selectedDate.getMonth() < self.currentMonth ||
                    selectedDate.getMonth() >
                        self.currentMonth + self.config.showMonths - 1) &&
                    self.config.mode !== "range";
                self.selectedDateElem = target;
                if (self.config.mode === "single")
                    self.selectedDates = [selectedDate];
                else if (self.config.mode === "multiple") {
                    var selectedIndex = isDateSelected(selectedDate);
                    if (selectedIndex)
                        self.selectedDates.splice(parseInt(selectedIndex), 1);
                    else
                        self.selectedDates.push(selectedDate);
                }
                else if (self.config.mode === "range") {
                    if (self.selectedDates.length === 2) {
                        self.clear(false, false);
                    }
                    self.latestSelectedDateObj = selectedDate;
                    self.selectedDates.push(selectedDate);
                    // unless selecting same date twice, sort ascendingly
                    if (compareDates(selectedDate, self.selectedDates[0], true) !== 0)
                        self.selectedDates.sort(function (a, b) { return a.getTime() - b.getTime(); });
                }
                setHoursFromInputs();
                if (shouldChangeMonth) {
                    var isNewYear = self.currentYear !== selectedDate.getFullYear();
                    self.currentYear = selectedDate.getFullYear();
                    self.currentMonth = selectedDate.getMonth();
                    if (isNewYear) {
                        triggerEvent("onYearChange");
                        buildMonthSwitch();
                    }
                    triggerEvent("onMonthChange");
                }
                updateNavigationCurrentMonth();
                buildDays();
                updateValue();
                // maintain focus
                if (!shouldChangeMonth &&
                    self.config.mode !== "range" &&
                    self.config.showMonths === 1)
                    focusOnDayElem(target);
                else if (self.selectedDateElem !== undefined &&
                    self.hourElement === undefined) {
                    self.selectedDateElem && self.selectedDateElem.focus();
                }
                if (self.hourElement !== undefined)
                    self.hourElement !== undefined && self.hourElement.focus();
                if (self.config.closeOnSelect) {
                    var single = self.config.mode === "single" && !self.config.enableTime;
                    var range = self.config.mode === "range" &&
                        self.selectedDates.length === 2 &&
                        !self.config.enableTime;
                    if (single || range) {
                        focusAndClose();
                    }
                }
                triggerChange();
            }
            var CALLBACKS = {
                locale: [setupLocale, updateWeekdays],
                showMonths: [buildMonths, setCalendarWidth, buildWeekdays],
                minDate: [jumpToDate],
                maxDate: [jumpToDate],
            };
            function set(option, value) {
                if (option !== null && typeof option === "object") {
                    Object.assign(self.config, option);
                    for (var key in option) {
                        if (CALLBACKS[key] !== undefined)
                            CALLBACKS[key].forEach(function (x) { return x(); });
                    }
                }
                else {
                    self.config[option] = value;
                    if (CALLBACKS[option] !== undefined)
                        CALLBACKS[option].forEach(function (x) { return x(); });
                    else if (HOOKS.indexOf(option) > -1)
                        self.config[option] = arrayify(value);
                }
                self.redraw();
                updateValue(true);
            }
            function setSelectedDate(inputDate, format) {
                var dates = [];
                if (inputDate instanceof Array)
                    dates = inputDate.map(function (d) { return self.parseDate(d, format); });
                else if (inputDate instanceof Date || typeof inputDate === "number")
                    dates = [self.parseDate(inputDate, format)];
                else if (typeof inputDate === "string") {
                    switch (self.config.mode) {
                        case "single":
                        case "time":
                            dates = [self.parseDate(inputDate, format)];
                            break;
                        case "multiple":
                            dates = inputDate
                                .split(self.config.conjunction)
                                .map(function (date) { return self.parseDate(date, format); });
                            break;
                        case "range":
                            dates = inputDate
                                .split(self.l10n.rangeSeparator)
                                .map(function (date) { return self.parseDate(date, format); });
                            break;
                    }
                }
                else
                    self.config.errorHandler(new Error("Invalid date supplied: " + JSON.stringify(inputDate)));
                self.selectedDates = (self.config.allowInvalidPreload
                    ? dates
                    : dates.filter(function (d) { return d instanceof Date && isEnabled(d, false); }));
                if (self.config.mode === "range")
                    self.selectedDates.sort(function (a, b) { return a.getTime() - b.getTime(); });
            }
            function setDate(date, triggerChange, format) {
                if (triggerChange === void 0) { triggerChange = false; }
                if (format === void 0) { format = self.config.dateFormat; }
                if ((date !== 0 && !date) || (date instanceof Array && date.length === 0))
                    return self.clear(triggerChange);
                setSelectedDate(date, format);
                self.latestSelectedDateObj =
                    self.selectedDates[self.selectedDates.length - 1];
                self.redraw();
                jumpToDate(undefined, triggerChange);
                setHoursFromDate();
                if (self.selectedDates.length === 0) {
                    self.clear(false);
                }
                updateValue(triggerChange);
                if (triggerChange)
                    triggerEvent("onChange");
            }
            function parseDateRules(arr) {
                return arr
                    .slice()
                    .map(function (rule) {
                    if (typeof rule === "string" ||
                        typeof rule === "number" ||
                        rule instanceof Date) {
                        return self.parseDate(rule, undefined, true);
                    }
                    else if (rule &&
                        typeof rule === "object" &&
                        rule.from &&
                        rule.to)
                        return {
                            from: self.parseDate(rule.from, undefined),
                            to: self.parseDate(rule.to, undefined),
                        };
                    return rule;
                })
                    .filter(function (x) { return x; }); // remove falsy values
            }
            function setupDates() {
                self.selectedDates = [];
                self.now = self.parseDate(self.config.now) || new Date();
                // Workaround IE11 setting placeholder as the input's value
                var preloadedDate = self.config.defaultDate ||
                    ((self.input.nodeName === "INPUT" ||
                        self.input.nodeName === "TEXTAREA") &&
                        self.input.placeholder &&
                        self.input.value === self.input.placeholder
                        ? null
                        : self.input.value);
                if (preloadedDate)
                    setSelectedDate(preloadedDate, self.config.dateFormat);
                self._initialDate =
                    self.selectedDates.length > 0
                        ? self.selectedDates[0]
                        : self.config.minDate &&
                            self.config.minDate.getTime() > self.now.getTime()
                            ? self.config.minDate
                            : self.config.maxDate &&
                                self.config.maxDate.getTime() < self.now.getTime()
                                ? self.config.maxDate
                                : self.now;
                self.currentYear = self._initialDate.getFullYear();
                self.currentMonth = self._initialDate.getMonth();
                if (self.selectedDates.length > 0)
                    self.latestSelectedDateObj = self.selectedDates[0];
                if (self.config.minTime !== undefined)
                    self.config.minTime = self.parseDate(self.config.minTime, "H:i");
                if (self.config.maxTime !== undefined)
                    self.config.maxTime = self.parseDate(self.config.maxTime, "H:i");
                self.minDateHasTime =
                    !!self.config.minDate &&
                        (self.config.minDate.getHours() > 0 ||
                            self.config.minDate.getMinutes() > 0 ||
                            self.config.minDate.getSeconds() > 0);
                self.maxDateHasTime =
                    !!self.config.maxDate &&
                        (self.config.maxDate.getHours() > 0 ||
                            self.config.maxDate.getMinutes() > 0 ||
                            self.config.maxDate.getSeconds() > 0);
            }
            function setupInputs() {
                self.input = getInputElem();
                /* istanbul ignore next */
                if (!self.input) {
                    self.config.errorHandler(new Error("Invalid input element specified"));
                    return;
                }
                // hack: store previous type to restore it after destroy()
                self.input._type = self.input.type;
                self.input.type = "text";
                self.input.classList.add("flatpickr-input");
                self._input = self.input;
                if (self.config.altInput) {
                    // replicate self.element
                    self.altInput = createElement(self.input.nodeName, self.config.altInputClass);
                    self._input = self.altInput;
                    self.altInput.placeholder = self.input.placeholder;
                    self.altInput.disabled = self.input.disabled;
                    self.altInput.required = self.input.required;
                    self.altInput.tabIndex = self.input.tabIndex;
                    self.altInput.type = "text";
                    self.input.setAttribute("type", "hidden");
                    if (!self.config.static && self.input.parentNode)
                        self.input.parentNode.insertBefore(self.altInput, self.input.nextSibling);
                }
                if (!self.config.allowInput)
                    self._input.setAttribute("readonly", "readonly");
                self._positionElement = self.config.positionElement || self._input;
            }
            function setupMobile() {
                var inputType = self.config.enableTime
                    ? self.config.noCalendar
                        ? "time"
                        : "datetime-local"
                    : "date";
                self.mobileInput = createElement("input", self.input.className + " flatpickr-mobile");
                self.mobileInput.tabIndex = 1;
                self.mobileInput.type = inputType;
                self.mobileInput.disabled = self.input.disabled;
                self.mobileInput.required = self.input.required;
                self.mobileInput.placeholder = self.input.placeholder;
                self.mobileFormatStr =
                    inputType === "datetime-local"
                        ? "Y-m-d\\TH:i:S"
                        : inputType === "date"
                            ? "Y-m-d"
                            : "H:i:S";
                if (self.selectedDates.length > 0) {
                    self.mobileInput.defaultValue = self.mobileInput.value = self.formatDate(self.selectedDates[0], self.mobileFormatStr);
                }
                if (self.config.minDate)
                    self.mobileInput.min = self.formatDate(self.config.minDate, "Y-m-d");
                if (self.config.maxDate)
                    self.mobileInput.max = self.formatDate(self.config.maxDate, "Y-m-d");
                if (self.input.getAttribute("step"))
                    self.mobileInput.step = String(self.input.getAttribute("step"));
                self.input.type = "hidden";
                if (self.altInput !== undefined)
                    self.altInput.type = "hidden";
                try {
                    if (self.input.parentNode)
                        self.input.parentNode.insertBefore(self.mobileInput, self.input.nextSibling);
                }
                catch (_a) { }
                bind(self.mobileInput, "change", function (e) {
                    self.setDate(getEventTarget(e).value, false, self.mobileFormatStr);
                    triggerEvent("onChange");
                    triggerEvent("onClose");
                });
            }
            function toggle(e) {
                if (self.isOpen === true)
                    return self.close();
                self.open(e);
            }
            function triggerEvent(event, data) {
                // If the instance has been destroyed already, all hooks have been removed
                if (self.config === undefined)
                    return;
                var hooks = self.config[event];
                if (hooks !== undefined && hooks.length > 0) {
                    for (var i = 0; hooks[i] && i < hooks.length; i++)
                        hooks[i](self.selectedDates, self.input.value, self, data);
                }
                if (event === "onChange") {
                    self.input.dispatchEvent(createEvent("change"));
                    // many front-end frameworks bind to the input event
                    self.input.dispatchEvent(createEvent("input"));
                }
            }
            function createEvent(name) {
                var e = document.createEvent("Event");
                e.initEvent(name, true, true);
                return e;
            }
            function isDateSelected(date) {
                for (var i = 0; i < self.selectedDates.length; i++) {
                    if (compareDates(self.selectedDates[i], date) === 0)
                        return "" + i;
                }
                return false;
            }
            function isDateInRange(date) {
                if (self.config.mode !== "range" || self.selectedDates.length < 2)
                    return false;
                return (compareDates(date, self.selectedDates[0]) >= 0 &&
                    compareDates(date, self.selectedDates[1]) <= 0);
            }
            function updateNavigationCurrentMonth() {
                if (self.config.noCalendar || self.isMobile || !self.monthNav)
                    return;
                self.yearElements.forEach(function (yearElement, i) {
                    var d = new Date(self.currentYear, self.currentMonth, 1);
                    d.setMonth(self.currentMonth + i);
                    if (self.config.showMonths > 1 ||
                        self.config.monthSelectorType === "static") {
                        self.monthElements[i].textContent =
                            monthToStr(d.getMonth(), self.config.shorthandCurrentMonth, self.l10n) + " ";
                    }
                    else {
                        self.monthsDropdownContainer.value = d.getMonth().toString();
                    }
                    yearElement.value = d.getFullYear().toString();
                });
                self._hidePrevMonthArrow =
                    self.config.minDate !== undefined &&
                        (self.currentYear === self.config.minDate.getFullYear()
                            ? self.currentMonth <= self.config.minDate.getMonth()
                            : self.currentYear < self.config.minDate.getFullYear());
                self._hideNextMonthArrow =
                    self.config.maxDate !== undefined &&
                        (self.currentYear === self.config.maxDate.getFullYear()
                            ? self.currentMonth + 1 > self.config.maxDate.getMonth()
                            : self.currentYear > self.config.maxDate.getFullYear());
            }
            function getDateStr(format) {
                return self.selectedDates
                    .map(function (dObj) { return self.formatDate(dObj, format); })
                    .filter(function (d, i, arr) {
                    return self.config.mode !== "range" ||
                        self.config.enableTime ||
                        arr.indexOf(d) === i;
                })
                    .join(self.config.mode !== "range"
                    ? self.config.conjunction
                    : self.l10n.rangeSeparator);
            }
            /**
             * Updates the values of inputs associated with the calendar
             */
            function updateValue(triggerChange) {
                if (triggerChange === void 0) { triggerChange = true; }
                if (self.mobileInput !== undefined && self.mobileFormatStr) {
                    self.mobileInput.value =
                        self.latestSelectedDateObj !== undefined
                            ? self.formatDate(self.latestSelectedDateObj, self.mobileFormatStr)
                            : "";
                }
                self.input.value = getDateStr(self.config.dateFormat);
                if (self.altInput !== undefined) {
                    self.altInput.value = getDateStr(self.config.altFormat);
                }
                if (triggerChange !== false)
                    triggerEvent("onValueUpdate");
            }
            function onMonthNavClick(e) {
                var eventTarget = getEventTarget(e);
                var isPrevMonth = self.prevMonthNav.contains(eventTarget);
                var isNextMonth = self.nextMonthNav.contains(eventTarget);
                if (isPrevMonth || isNextMonth) {
                    changeMonth(isPrevMonth ? -1 : 1);
                }
                else if (self.yearElements.indexOf(eventTarget) >= 0) {
                    eventTarget.select();
                }
                else if (eventTarget.classList.contains("arrowUp")) {
                    self.changeYear(self.currentYear + 1);
                }
                else if (eventTarget.classList.contains("arrowDown")) {
                    self.changeYear(self.currentYear - 1);
                }
            }
            function timeWrapper(e) {
                e.preventDefault();
                var isKeyDown = e.type === "keydown", eventTarget = getEventTarget(e), input = eventTarget;
                if (self.amPM !== undefined && eventTarget === self.amPM) {
                    self.amPM.textContent =
                        self.l10n.amPM[int(self.amPM.textContent === self.l10n.amPM[0])];
                }
                var min = parseFloat(input.getAttribute("min")), max = parseFloat(input.getAttribute("max")), step = parseFloat(input.getAttribute("step")), curValue = parseInt(input.value, 10), delta = e.delta ||
                    (isKeyDown ? (e.which === 38 ? 1 : -1) : 0);
                var newValue = curValue + step * delta;
                if (typeof input.value !== "undefined" && input.value.length === 2) {
                    var isHourElem = input === self.hourElement, isMinuteElem = input === self.minuteElement;
                    if (newValue < min) {
                        newValue =
                            max +
                                newValue +
                                int(!isHourElem) +
                                (int(isHourElem) && int(!self.amPM));
                        if (isMinuteElem)
                            incrementNumInput(undefined, -1, self.hourElement);
                    }
                    else if (newValue > max) {
                        newValue =
                            input === self.hourElement ? newValue - max - int(!self.amPM) : min;
                        if (isMinuteElem)
                            incrementNumInput(undefined, 1, self.hourElement);
                    }
                    if (self.amPM &&
                        isHourElem &&
                        (step === 1
                            ? newValue + curValue === 23
                            : Math.abs(newValue - curValue) > step)) {
                        self.amPM.textContent =
                            self.l10n.amPM[int(self.amPM.textContent === self.l10n.amPM[0])];
                    }
                    input.value = pad(newValue);
                }
            }
            init();
            return self;
        }
        /* istanbul ignore next */
        function _flatpickr(nodeList, config) {
            // static list
            var nodes = Array.prototype.slice
                .call(nodeList)
                .filter(function (x) { return x instanceof HTMLElement; });
            var instances = [];
            for (var i = 0; i < nodes.length; i++) {
                var node = nodes[i];
                try {
                    if (node.getAttribute("data-fp-omit") !== null)
                        continue;
                    if (node._flatpickr !== undefined) {
                        node._flatpickr.destroy();
                        node._flatpickr = undefined;
                    }
                    node._flatpickr = FlatpickrInstance(node, config || {});
                    instances.push(node._flatpickr);
                }
                catch (e) {
                    console.error(e);
                }
            }
            return instances.length === 1 ? instances[0] : instances;
        }
        /* istanbul ignore next */
        if (typeof HTMLElement !== "undefined" &&
            typeof HTMLCollection !== "undefined" &&
            typeof NodeList !== "undefined") {
            // browser env
            HTMLCollection.prototype.flatpickr = NodeList.prototype.flatpickr = function (config) {
                return _flatpickr(this, config);
            };
            HTMLElement.prototype.flatpickr = function (config) {
                return _flatpickr([this], config);
            };
        }
        /* istanbul ignore next */
        var flatpickr = function (selector, config) {
            if (typeof selector === "string") {
                return _flatpickr(window.document.querySelectorAll(selector), config);
            }
            else if (selector instanceof Node) {
                return _flatpickr([selector], config);
            }
            else {
                return _flatpickr(selector, config);
            }
        };
        /* istanbul ignore next */
        flatpickr.defaultConfig = {};
        flatpickr.l10ns = {
            en: __assign({}, english),
            default: __assign({}, english),
        };
        flatpickr.localize = function (l10n) {
            flatpickr.l10ns.default = __assign(__assign({}, flatpickr.l10ns.default), l10n);
        };
        flatpickr.setDefaults = function (config) {
            flatpickr.defaultConfig = __assign(__assign({}, flatpickr.defaultConfig), config);
        };
        flatpickr.parseDate = createDateParser({});
        flatpickr.formatDate = createDateFormatter({});
        flatpickr.compareDates = compareDates;
        /* istanbul ignore next */
        if (typeof jQuery !== "undefined" && typeof jQuery.fn !== "undefined") {
            jQuery.fn.flatpickr = function (config) {
                return _flatpickr(this, config);
            };
        }
        // eslint-disable-next-line @typescript-eslint/camelcase
        Date.prototype.fp_incr = function (days) {
            return new Date(this.getFullYear(), this.getMonth(), this.getDate() + (typeof days === "string" ? parseInt(days, 10) : days));
        };
        if (typeof window !== "undefined") {
            window.flatpickr = flatpickr;
        }

        return flatpickr;

    })));
    });

    /* node_modules/svelte-flatpickr/src/Flatpickr.svelte generated by Svelte v3.29.4 */
    const file$3 = "node_modules/svelte-flatpickr/src/Flatpickr.svelte";

    // (1:6)    
    function fallback_block(ctx) {
    	let input_1;
    	let input_1_levels = [/*props*/ ctx[1]];
    	let input_1_data = {};

    	for (let i = 0; i < input_1_levels.length; i += 1) {
    		input_1_data = assign(input_1_data, input_1_levels[i]);
    	}

    	const block = {
    		c: function create() {
    			input_1 = element("input");
    			set_attributes(input_1, input_1_data);
    			add_location(input_1, file$3, 1, 2, 9);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, input_1, anchor);
    			/*input_1_binding*/ ctx[8](input_1);
    		},
    		p: function update(ctx, dirty) {
    			set_attributes(input_1, input_1_data = get_spread_update(input_1_levels, [/*props*/ ctx[1]]));
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(input_1);
    			/*input_1_binding*/ ctx[8](null);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: fallback_block.name,
    		type: "fallback",
    		source: "(1:6)    ",
    		ctx
    	});

    	return block;
    }

    function create_fragment$4(ctx) {
    	let current;
    	const default_slot_template = /*#slots*/ ctx[7].default;
    	const default_slot = create_slot(default_slot_template, ctx, /*$$scope*/ ctx[6], null);
    	const default_slot_or_fallback = default_slot || fallback_block(ctx);

    	const block = {
    		c: function create() {
    			if (default_slot_or_fallback) default_slot_or_fallback.c();
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			if (default_slot_or_fallback) {
    				default_slot_or_fallback.m(target, anchor);
    			}

    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			if (default_slot) {
    				if (default_slot.p && dirty & /*$$scope*/ 64) {
    					update_slot(default_slot, default_slot_template, ctx, /*$$scope*/ ctx[6], dirty, null, null);
    				}
    			} else {
    				if (default_slot_or_fallback && default_slot_or_fallback.p && dirty & /*input*/ 1) {
    					default_slot_or_fallback.p(ctx, dirty);
    				}
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(default_slot_or_fallback, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(default_slot_or_fallback, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (default_slot_or_fallback) default_slot_or_fallback.d(detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$4.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function stripOn(hook) {
    	return hook.charAt(2).toLowerCase() + hook.substring(3);
    }

    function instance$4($$self, $$props, $$invalidate) {
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots("Flatpickr", slots, ['default']);

    	const hooks = new Set([
    			"onChange",
    			"onOpen",
    			"onClose",
    			"onMonthChange",
    			"onYearChange",
    			"onReady",
    			"onValueUpdate",
    			"onDayCreate"
    		]);

    	let { value = "" } = $$props;
    	let { formattedValue = "" } = $$props;
    	let { element = null } = $$props;
    	let { dateFormat = null } = $$props;
    	let allProps = $$props;
    	const options = allProps.options || {};
    	const props = Object.assign({}, $$props);
    	delete props.options;
    	let input, fp;

    	onMount(() => {
    		const elem = element || input;
    		$$invalidate(9, fp = flatpickr(elem, Object.assign(addHooks(options), element ? { wrap: true } : {})));

    		return () => {
    			fp.destroy();
    		};
    	});

    	const dispatch = createEventDispatcher();

    	function addHooks(opts = {}) {
    		opts = Object.assign({}, opts);

    		for (const hook of hooks) {
    			const firer = (selectedDates, dateStr, instance) => {
    				dispatch(stripOn(hook), [selectedDates, dateStr, instance]);
    			};

    			if (hook in opts) {
    				// Hooks must be arrays
    				if (!Array.isArray(opts[hook])) opts[hook] = [opts[hook]];

    				opts[hook].push(firer);
    			} else {
    				opts[hook] = [firer];
    			}
    		}

    		if (opts.onChange && !opts.onChange.includes(updateValue)) opts.onChange.push(updateValue);
    		return opts;
    	}

    	function updateValue(newValue, dateStr) {
    		$$invalidate(2, value = Array.isArray(newValue) && newValue.length === 1
    		? newValue[0]
    		: newValue);

    		$$invalidate(3, formattedValue = dateStr);
    	}

    	function input_1_binding($$value) {
    		binding_callbacks[$$value ? "unshift" : "push"](() => {
    			input = $$value;
    			$$invalidate(0, input);
    		});
    	}

    	$$self.$$set = $$new_props => {
    		$$invalidate(16, $$props = assign(assign({}, $$props), exclude_internal_props($$new_props)));
    		if ("value" in $$new_props) $$invalidate(2, value = $$new_props.value);
    		if ("formattedValue" in $$new_props) $$invalidate(3, formattedValue = $$new_props.formattedValue);
    		if ("element" in $$new_props) $$invalidate(4, element = $$new_props.element);
    		if ("dateFormat" in $$new_props) $$invalidate(5, dateFormat = $$new_props.dateFormat);
    		if ("$$scope" in $$new_props) $$invalidate(6, $$scope = $$new_props.$$scope);
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		createEventDispatcher,
    		flatpickr,
    		hooks,
    		value,
    		formattedValue,
    		element,
    		dateFormat,
    		allProps,
    		options,
    		props,
    		input,
    		fp,
    		dispatch,
    		addHooks,
    		updateValue,
    		stripOn
    	});

    	$$self.$inject_state = $$new_props => {
    		$$invalidate(16, $$props = assign(assign({}, $$props), $$new_props));
    		if ("value" in $$props) $$invalidate(2, value = $$new_props.value);
    		if ("formattedValue" in $$props) $$invalidate(3, formattedValue = $$new_props.formattedValue);
    		if ("element" in $$props) $$invalidate(4, element = $$new_props.element);
    		if ("dateFormat" in $$props) $$invalidate(5, dateFormat = $$new_props.dateFormat);
    		if ("allProps" in $$props) allProps = $$new_props.allProps;
    		if ("input" in $$props) $$invalidate(0, input = $$new_props.input);
    		if ("fp" in $$props) $$invalidate(9, fp = $$new_props.fp);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*fp, value, dateFormat*/ 548) {
    			 if (fp) fp.setDate(value, false, dateFormat);
    		}

    		if ($$self.$$.dirty & /*fp*/ 512) {
    			 if (fp) for (const [key, val] of Object.entries(addHooks(options))) {
    				fp.set(key, val);
    			}
    		}
    	};

    	$$props = exclude_internal_props($$props);

    	return [
    		input,
    		props,
    		value,
    		formattedValue,
    		element,
    		dateFormat,
    		$$scope,
    		slots,
    		input_1_binding
    	];
    }

    class Flatpickr extends SvelteComponentDev {
    	constructor(options) {
    		super(options);

    		init(this, options, instance$4, create_fragment$4, safe_not_equal, {
    			value: 2,
    			formattedValue: 3,
    			element: 4,
    			dateFormat: 5
    		});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Flatpickr",
    			options,
    			id: create_fragment$4.name
    		});
    	}

    	get value() {
    		throw new Error("<Flatpickr>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set value(value) {
    		throw new Error("<Flatpickr>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get formattedValue() {
    		throw new Error("<Flatpickr>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set formattedValue(value) {
    		throw new Error("<Flatpickr>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get element() {
    		throw new Error("<Flatpickr>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set element(value) {
    		throw new Error("<Flatpickr>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get dateFormat() {
    		throw new Error("<Flatpickr>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set dateFormat(value) {
    		throw new Error("<Flatpickr>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    var fr$1 = createCommonjsModule(function (module, exports) {
    (function (global, factory) {
       factory(exports) ;
    }(commonjsGlobal, (function (exports) {
      var fp = typeof window !== "undefined" && window.flatpickr !== undefined
          ? window.flatpickr
          : {
              l10ns: {},
          };
      var French = {
          firstDayOfWeek: 1,
          weekdays: {
              shorthand: ["dim", "lun", "mar", "mer", "jeu", "ven", "sam"],
              longhand: [
                  "dimanche",
                  "lundi",
                  "mardi",
                  "mercredi",
                  "jeudi",
                  "vendredi",
                  "samedi",
              ],
          },
          months: {
              shorthand: [
                  "janv",
                  "févr",
                  "mars",
                  "avr",
                  "mai",
                  "juin",
                  "juil",
                  "août",
                  "sept",
                  "oct",
                  "nov",
                  "déc",
              ],
              longhand: [
                  "janvier",
                  "février",
                  "mars",
                  "avril",
                  "mai",
                  "juin",
                  "juillet",
                  "août",
                  "septembre",
                  "octobre",
                  "novembre",
                  "décembre",
              ],
          },
          ordinal: function (nth) {
              if (nth > 1)
                  return "";
              return "er";
          },
          rangeSeparator: " au ",
          weekAbbreviation: "Sem",
          scrollTitle: "Défiler pour augmenter la valeur",
          toggleTitle: "Cliquer pour basculer",
          time_24hr: true,
      };
      fp.l10ns.fr = French;
      var fr = fp.l10ns;

      exports.French = French;
      exports.default = fr;

      Object.defineProperty(exports, '__esModule', { value: true });

    })));
    });

    var French = unwrapExports(fr$1);

    /* src/DatePicker.svelte generated by Svelte v3.29.4 */

    const { console: console_1 } = globals;
    const file$4 = "src/DatePicker.svelte";

    // (1673:0) <Flatpickr options={flatpickrOptionsRange} element="#my-picker" class="form-control datepicker bg-white" defaultDate={dates.range} placeholder={dates.range} >
    function create_default_slot(ctx) {
    	let div;
    	let input;
    	let input_placeholder_value;
    	let t0;
    	let button;
    	let t1_value = /*$_*/ ctx[0]("flatpickr.button_clear", { default: "Clear" }) + "";
    	let t1;
    	let mounted;
    	let dispose;

    	const block = {
    		c: function create() {
    			div = element("div");
    			input = element("input");
    			t0 = space();
    			button = element("button");
    			t1 = text(t1_value);
    			attr_dev(input, "type", "text");
    			attr_dev(input, "placeholder", input_placeholder_value = /*$_*/ ctx[0]("flatpickr.select", { default: "Select dates.." }));
    			attr_dev(input, "data-input", "");
    			add_location(input, file$4, 1681, 0, 45753);
    			attr_dev(button, "type", "button");
    			attr_dev(button, "class", "btn btn-primary input-button");
    			attr_dev(button, "data-clear", "");
    			add_location(button, file$4, 1683, 0, 45855);
    			attr_dev(div, "class", "flatpickr");
    			attr_dev(div, "id", "my-picker");
    			add_location(div, file$4, 1680, 0, 45714);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div, anchor);
    			append_dev(div, input);
    			append_dev(div, t0);
    			append_dev(div, button);
    			append_dev(button, t1);

    			if (!mounted) {
    				dispose = listen_dev(button, "click", /*reset*/ ctx[3], false, false, false);
    				mounted = true;
    			}
    		},
    		p: function update(ctx, dirty) {
    			if (dirty & /*$_*/ 1 && input_placeholder_value !== (input_placeholder_value = /*$_*/ ctx[0]("flatpickr.select", { default: "Select dates.." }))) {
    				attr_dev(input, "placeholder", input_placeholder_value);
    			}

    			if (dirty & /*$_*/ 1 && t1_value !== (t1_value = /*$_*/ ctx[0]("flatpickr.button_clear", { default: "Clear" }) + "")) set_data_dev(t1, t1_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div);
    			mounted = false;
    			dispose();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_default_slot.name,
    		type: "slot",
    		source: "(1673:0) <Flatpickr options={flatpickrOptionsRange} element=\\\"#my-picker\\\" class=\\\"form-control datepicker bg-white\\\" defaultDate={dates.range} placeholder={dates.range} >",
    		ctx
    	});

    	return block;
    }

    function create_fragment$5(ctx) {
    	let flatpickr;
    	let current;

    	flatpickr = new Flatpickr({
    			props: {
    				options: /*flatpickrOptionsRange*/ ctx[2],
    				element: "#my-picker",
    				class: "form-control datepicker bg-white",
    				defaultDate: /*dates*/ ctx[1].range,
    				placeholder: /*dates*/ ctx[1].range,
    				$$slots: { default: [create_default_slot] },
    				$$scope: { ctx }
    			},
    			$$inline: true
    		});

    	const block = {
    		c: function create() {
    			create_component(flatpickr.$$.fragment);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			mount_component(flatpickr, target, anchor);
    			current = true;
    		},
    		p: function update(ctx, [dirty]) {
    			const flatpickr_changes = {};

    			if (dirty & /*$$scope, $_*/ 4097) {
    				flatpickr_changes.$$scope = { dirty, ctx };
    			}

    			flatpickr.$set(flatpickr_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(flatpickr.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(flatpickr.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(flatpickr, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$5.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$5($$self, $$props, $$invalidate) {
    	let $_;
    	validate_store(nn, "_");
    	component_subscribe($$self, nn, $$value => $$invalidate(0, $_ = $$value));
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots("DatePicker", slots, []);
    	let { from_datetime_query = "" } = $$props;
    	let { to_datetime_query = "" } = $$props;
    	let myElement;
    	let epoch = "2012-06-06";
    	let from_datetime = "";
    	let to_datetime = "";
    	let now = new Date();

    	let dates = {
    		simple: new Date(),
    		range: epoch + " to " + now.toISOString().slice(0, 10)
    	};

    	function getLocale() {
    		// getLocaleFromNavigator returns fr-FR
    		// we need to set locale to fr
    		var extLocale = M();

    		var shortLocale = extLocale.substring(0, extLocale.indexOf("-"));
    		return shortLocale;
    	}

    	const flatpickrOptionsRange = {
    		mode: "range",
    		locale: getLocale(),
    		element: "#my-picker",
    		enableTime: true,
    		onChange: (selectedDates, dateStr, instance) => {
    			/*console.log(`Options onChange handler:\n \
    selectedDates: ${selectedDates} ${typeof(selectedDates[0])} \n \
    dateStr: ${dateStr} ${typeof(dateStr)}`)*/
    			try {
    				if (selectedDates.length > 1) {
    					from_datetime = selectedDates[0].toISOString();

    					//console.log(`from_datetime: ${from_datetime}`);
    					to_datetime = selectedDates[1].toISOString();
    				} //console.log(`to_datetime: ${to_datetime}`);
    			} catch(error) {
    				console.error(error);
    			} // expected output: ReferenceError: nonExistentFunction is not defined

    			try {
    				if (from_datetime.length > 0) {
    					$$invalidate(4, from_datetime_query = `&from_datetime=${from_datetime}`);
    				}

    				if (to_datetime.length > 0) {
    					$$invalidate(5, to_datetime_query = `&to_datetime=${to_datetime}`);
    				}
    			} catch(error) {
    				console.log(error);
    			}
    		}
    	};

    	function reset() {
    		from_datetime = epoch;
    		$$invalidate(4, from_datetime_query = `&from_datetime=${epoch}`);
    		var now = new Date();
    		to_datetime = now.toISOString().slice(0, 10);
    		$$invalidate(5, to_datetime_query = `&to_datetime=${to_datetime}`);
    	}

    	const writable_props = ["from_datetime_query", "to_datetime_query"];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console_1.warn(`<DatePicker> was created with unknown prop '${key}'`);
    	});

    	$$self.$$set = $$props => {
    		if ("from_datetime_query" in $$props) $$invalidate(4, from_datetime_query = $$props.from_datetime_query);
    		if ("to_datetime_query" in $$props) $$invalidate(5, to_datetime_query = $$props.to_datetime_query);
    	};

    	$$self.$capture_state = () => ({
    		FlatpickrCss,
    		Flatpickr,
    		French,
    		_: nn,
    		getLocaleFromNavigator: M,
    		from_datetime_query,
    		to_datetime_query,
    		myElement,
    		epoch,
    		from_datetime,
    		to_datetime,
    		now,
    		dates,
    		getLocale,
    		flatpickrOptionsRange,
    		reset,
    		$_
    	});

    	$$self.$inject_state = $$props => {
    		if ("from_datetime_query" in $$props) $$invalidate(4, from_datetime_query = $$props.from_datetime_query);
    		if ("to_datetime_query" in $$props) $$invalidate(5, to_datetime_query = $$props.to_datetime_query);
    		if ("myElement" in $$props) myElement = $$props.myElement;
    		if ("epoch" in $$props) epoch = $$props.epoch;
    		if ("from_datetime" in $$props) from_datetime = $$props.from_datetime;
    		if ("to_datetime" in $$props) to_datetime = $$props.to_datetime;
    		if ("now" in $$props) now = $$props.now;
    		if ("dates" in $$props) $$invalidate(1, dates = $$props.dates);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [
    		$_,
    		dates,
    		flatpickrOptionsRange,
    		reset,
    		from_datetime_query,
    		to_datetime_query
    	];
    }

    class DatePicker extends SvelteComponentDev {
    	constructor(options) {
    		super(options);

    		init(this, options, instance$5, create_fragment$5, safe_not_equal, {
    			from_datetime_query: 4,
    			to_datetime_query: 5
    		});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "DatePicker",
    			options,
    			id: create_fragment$5.name
    		});
    	}

    	get from_datetime_query() {
    		throw new Error("<DatePicker>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set from_datetime_query(value) {
    		throw new Error("<DatePicker>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get to_datetime_query() {
    		throw new Error("<DatePicker>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set to_datetime_query(value) {
    		throw new Error("<DatePicker>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    var all_items_loaded_yes = "All items are loaded.";
    var all_items_loaded_no = "Not all items are loaded: keep scrolling!";
    var no_item_found = "No item found.";
    var yes = "Yes";
    var no = "No";
    var status_categories = "Categories";
    var status_tags = "Tags";
    var select_all = "Select all";
    var uncategorized = "not categorized";
    var uncategorized_summary = "Does not belong to any category.";
    var view_on_twitter = "View on Twitter";
    var flatpickr$1 = {
    	button_clear: "Clear",
    	select: "Select dates.."
    };
    var en$2 = {
    	all_items_loaded_yes: all_items_loaded_yes,
    	all_items_loaded_no: all_items_loaded_no,
    	no_item_found: no_item_found,
    	yes: yes,
    	no: no,
    	status_categories: status_categories,
    	status_tags: status_tags,
    	select_all: select_all,
    	uncategorized: uncategorized,
    	uncategorized_summary: uncategorized_summary,
    	view_on_twitter: view_on_twitter,
    	flatpickr: flatpickr$1
    };

    var yes$1 = "Oui";
    var no$1 = "Non";
    var all_items_loaded_yes$1 = "Tous les éléments sont chargés.";
    var all_items_loaded_no$1 = "Tous les éléments ne sont pas chargés: continuez à faire défiler!";
    var no_item_found$1 = "Aucun élément trouvé.";
    var status_categories$1 = "Catégories";
    var status_tags$1 = "Étiquettes";
    var select_all$1 = "Tout sélectionner";
    var uncategorized$1 = "sans catégorie";
    var uncategorized_summary$1 = "N'appartient à aucune catégorie.";
    var view_on_twitter$1 = "Voir sur Twitter";
    var flatpickr$2 = {
    	button_clear: "Effacer",
    	select: "Filtrer selon la date.."
    };
    var fr$2 = {
    	yes: yes$1,
    	no: no$1,
    	all_items_loaded_yes: all_items_loaded_yes$1,
    	all_items_loaded_no: all_items_loaded_no$1,
    	no_item_found: no_item_found$1,
    	status_categories: status_categories$1,
    	status_tags: status_tags$1,
    	select_all: select_all$1,
    	uncategorized: uncategorized$1,
    	uncategorized_summary: uncategorized_summary$1,
    	view_on_twitter: view_on_twitter$1,
    	flatpickr: flatpickr$2
    };

    /* src/App.svelte generated by Svelte v3.29.4 */

    const { Error: Error_1 } = globals;
    const file$5 = "src/App.svelte";

    function get_each_context$2(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[35] = list[i];
    	return child_ctx;
    }

    // (225:6) {#if has_api_access("search_category")}
    function create_if_block_3$1(ctx) {
    	let categories_1;
    	let updating_categories;
    	let updating_selected_categories;
    	let updating_query;
    	let current;

    	function categories_1_categories_binding(value) {
    		/*categories_1_categories_binding*/ ctx[14].call(null, value);
    	}

    	function categories_1_selected_categories_binding(value) {
    		/*categories_1_selected_categories_binding*/ ctx[15].call(null, value);
    	}

    	function categories_1_query_binding(value) {
    		/*categories_1_query_binding*/ ctx[16].call(null, value);
    	}

    	let categories_1_props = {
    		title: /*$_*/ ctx[10]("status_categories"),
    		id: "cat"
    	};

    	if (/*categories*/ ctx[1] !== void 0) {
    		categories_1_props.categories = /*categories*/ ctx[1];
    	}

    	if (/*selected_categories*/ ctx[3] !== void 0) {
    		categories_1_props.selected_categories = /*selected_categories*/ ctx[3];
    	}

    	if (/*cat_query*/ ctx[5] !== void 0) {
    		categories_1_props.query = /*cat_query*/ ctx[5];
    	}

    	categories_1 = new Categories({
    			props: categories_1_props,
    			$$inline: true
    		});

    	binding_callbacks.push(() => bind(categories_1, "categories", categories_1_categories_binding));
    	binding_callbacks.push(() => bind(categories_1, "selected_categories", categories_1_selected_categories_binding));
    	binding_callbacks.push(() => bind(categories_1, "query", categories_1_query_binding));

    	const block = {
    		c: function create() {
    			create_component(categories_1.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(categories_1, target, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const categories_1_changes = {};
    			if (dirty[0] & /*$_*/ 1024) categories_1_changes.title = /*$_*/ ctx[10]("status_categories");

    			if (!updating_categories && dirty[0] & /*categories*/ 2) {
    				updating_categories = true;
    				categories_1_changes.categories = /*categories*/ ctx[1];
    				add_flush_callback(() => updating_categories = false);
    			}

    			if (!updating_selected_categories && dirty[0] & /*selected_categories*/ 8) {
    				updating_selected_categories = true;
    				categories_1_changes.selected_categories = /*selected_categories*/ ctx[3];
    				add_flush_callback(() => updating_selected_categories = false);
    			}

    			if (!updating_query && dirty[0] & /*cat_query*/ 32) {
    				updating_query = true;
    				categories_1_changes.query = /*cat_query*/ ctx[5];
    				add_flush_callback(() => updating_query = false);
    			}

    			categories_1.$set(categories_1_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(categories_1.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(categories_1.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(categories_1, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_3$1.name,
    		type: "if",
    		source: "(225:6) {#if has_api_access(\\\"search_category\\\")}",
    		ctx
    	});

    	return block;
    }

    // (233:6) {#if has_api_access("search_tag")}
    function create_if_block_2$1(ctx) {
    	let categories_1;
    	let updating_selected_categories;
    	let updating_query;
    	let current;

    	function categories_1_selected_categories_binding_1(value) {
    		/*categories_1_selected_categories_binding_1*/ ctx[17].call(null, value);
    	}

    	function categories_1_query_binding_1(value) {
    		/*categories_1_query_binding_1*/ ctx[18].call(null, value);
    	}

    	let categories_1_props = {
    		categories: /*tags*/ ctx[2],
    		title: /*$_*/ ctx[10]("status_tags"),
    		id: "tag"
    	};

    	if (/*selected_tags*/ ctx[4] !== void 0) {
    		categories_1_props.selected_categories = /*selected_tags*/ ctx[4];
    	}

    	if (/*tag_query*/ ctx[6] !== void 0) {
    		categories_1_props.query = /*tag_query*/ ctx[6];
    	}

    	categories_1 = new Categories({
    			props: categories_1_props,
    			$$inline: true
    		});

    	binding_callbacks.push(() => bind(categories_1, "selected_categories", categories_1_selected_categories_binding_1));
    	binding_callbacks.push(() => bind(categories_1, "query", categories_1_query_binding_1));

    	const block = {
    		c: function create() {
    			create_component(categories_1.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(categories_1, target, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const categories_1_changes = {};
    			if (dirty[0] & /*tags*/ 4) categories_1_changes.categories = /*tags*/ ctx[2];
    			if (dirty[0] & /*$_*/ 1024) categories_1_changes.title = /*$_*/ ctx[10]("status_tags");

    			if (!updating_selected_categories && dirty[0] & /*selected_tags*/ 16) {
    				updating_selected_categories = true;
    				categories_1_changes.selected_categories = /*selected_tags*/ ctx[4];
    				add_flush_callback(() => updating_selected_categories = false);
    			}

    			if (!updating_query && dirty[0] & /*tag_query*/ 64) {
    				updating_query = true;
    				categories_1_changes.query = /*tag_query*/ ctx[6];
    				add_flush_callback(() => updating_query = false);
    			}

    			categories_1.$set(categories_1_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(categories_1.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(categories_1.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(categories_1, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_2$1.name,
    		type: "if",
    		source: "(233:6) {#if has_api_access(\\\"search_tag\\\")}",
    		ctx
    	});

    	return block;
    }

    // (241:6) {#if has_api_access("search_datetime")}
    function create_if_block_1$1(ctx) {
    	let datepicker;
    	let updating_from_datetime_query;
    	let updating_to_datetime_query;
    	let current;

    	function datepicker_from_datetime_query_binding(value) {
    		/*datepicker_from_datetime_query_binding*/ ctx[19].call(null, value);
    	}

    	function datepicker_to_datetime_query_binding(value) {
    		/*datepicker_to_datetime_query_binding*/ ctx[20].call(null, value);
    	}

    	let datepicker_props = {};

    	if (/*from_datetime_query*/ ctx[8] !== void 0) {
    		datepicker_props.from_datetime_query = /*from_datetime_query*/ ctx[8];
    	}

    	if (/*to_datetime_query*/ ctx[9] !== void 0) {
    		datepicker_props.to_datetime_query = /*to_datetime_query*/ ctx[9];
    	}

    	datepicker = new DatePicker({ props: datepicker_props, $$inline: true });
    	binding_callbacks.push(() => bind(datepicker, "from_datetime_query", datepicker_from_datetime_query_binding));
    	binding_callbacks.push(() => bind(datepicker, "to_datetime_query", datepicker_to_datetime_query_binding));

    	const block = {
    		c: function create() {
    			create_component(datepicker.$$.fragment);
    		},
    		m: function mount(target, anchor) {
    			mount_component(datepicker, target, anchor);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const datepicker_changes = {};

    			if (!updating_from_datetime_query && dirty[0] & /*from_datetime_query*/ 256) {
    				updating_from_datetime_query = true;
    				datepicker_changes.from_datetime_query = /*from_datetime_query*/ ctx[8];
    				add_flush_callback(() => updating_from_datetime_query = false);
    			}

    			if (!updating_to_datetime_query && dirty[0] & /*to_datetime_query*/ 512) {
    				updating_to_datetime_query = true;
    				datepicker_changes.to_datetime_query = /*to_datetime_query*/ ctx[9];
    				add_flush_callback(() => updating_to_datetime_query = false);
    			}

    			datepicker.$set(datepicker_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(datepicker.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(datepicker.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			destroy_component(datepicker, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block_1$1.name,
    		type: "if",
    		source: "(241:6) {#if has_api_access(\\\"search_datetime\\\")}",
    		ctx
    	});

    	return block;
    }

    // (250:8) {#each data as item}
    function create_each_block$2(ctx) {
    	let li;
    	let status;
    	let current;

    	status = new Status({
    			props: {
    				status: /*item*/ ctx[35],
    				baseURL: /*baseURL*/ ctx[11]
    			},
    			$$inline: true
    		});

    	const block = {
    		c: function create() {
    			li = element("li");
    			create_component(status.$$.fragment);
    			attr_dev(li, "class", "list-group-item svelte-1uhirki");
    			add_location(li, file$5, 250, 8, 6456);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, li, anchor);
    			mount_component(status, li, null);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			const status_changes = {};
    			if (dirty[0] & /*data*/ 1) status_changes.status = /*item*/ ctx[35];
    			status.$set(status_changes);
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(status.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(status.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(li);
    			destroy_component(status);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$2.name,
    		type: "each",
    		source: "(250:8) {#each data as item}",
    		ctx
    	});

    	return block;
    }

    // (264:6) {:else}
    function create_else_block(ctx) {
    	let t_value = /*$_*/ ctx[10]("no_item_found") + "";
    	let t;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty[0] & /*$_*/ 1024 && t_value !== (t_value = /*$_*/ ctx[10]("no_item_found") + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_else_block.name,
    		type: "else",
    		source: "(264:6) {:else}",
    		ctx
    	});

    	return block;
    }

    // (262:6) {#if data.length}
    function create_if_block$2(ctx) {
    	let t_value = (/*hasMore*/ ctx[7]
    	? /*$_*/ ctx[10]("all_items_loaded_no")
    	: /*$_*/ ctx[10]("all_items_loaded_yes")) + "";

    	let t;

    	const block = {
    		c: function create() {
    			t = text(t_value);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, t, anchor);
    		},
    		p: function update(ctx, dirty) {
    			if (dirty[0] & /*hasMore, $_*/ 1152 && t_value !== (t_value = (/*hasMore*/ ctx[7]
    			? /*$_*/ ctx[10]("all_items_loaded_no")
    			: /*$_*/ ctx[10]("all_items_loaded_yes")) + "")) set_data_dev(t, t_value);
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(t);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_if_block$2.name,
    		type: "if",
    		source: "(262:6) {#if data.length}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$6(ctx) {
    	let div3;
    	let div2;
    	let div0;
    	let show_if_2 = /*has_api_access*/ ctx[13]("search_category");
    	let t0;
    	let show_if_1 = /*has_api_access*/ ctx[13]("search_tag");
    	let t1;
    	let show_if = /*has_api_access*/ ctx[13]("search_datetime");
    	let t2;
    	let div1;
    	let ul;
    	let t3;
    	let infinitescroll;
    	let updating_hasMore;
    	let t4;
    	let p;
    	let current;
    	let if_block0 = show_if_2 && create_if_block_3$1(ctx);
    	let if_block1 = show_if_1 && create_if_block_2$1(ctx);
    	let if_block2 = show_if && create_if_block_1$1(ctx);
    	let each_value = /*data*/ ctx[0];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$2(get_each_context$2(ctx, each_value, i));
    	}

    	const out = i => transition_out(each_blocks[i], 1, 1, () => {
    		each_blocks[i] = null;
    	});

    	function infinitescroll_hasMore_binding(value) {
    		/*infinitescroll_hasMore_binding*/ ctx[21].call(null, value);
    	}

    	let infinitescroll_props = { threshold: "10" };

    	if (/*hasMore*/ ctx[7] !== void 0) {
    		infinitescroll_props.hasMore = /*hasMore*/ ctx[7];
    	}

    	infinitescroll = new InfiniteScroll({
    			props: infinitescroll_props,
    			$$inline: true
    		});

    	binding_callbacks.push(() => bind(infinitescroll, "hasMore", infinitescroll_hasMore_binding));
    	infinitescroll.$on("loadMore", /*loadMore_handler*/ ctx[22]);

    	function select_block_type(ctx, dirty) {
    		if (/*data*/ ctx[0].length) return create_if_block$2;
    		return create_else_block;
    	}

    	let current_block_type = select_block_type(ctx);
    	let if_block3 = current_block_type(ctx);

    	const block = {
    		c: function create() {
    			div3 = element("div");
    			div2 = element("div");
    			div0 = element("div");
    			if (if_block0) if_block0.c();
    			t0 = space();
    			if (if_block1) if_block1.c();
    			t1 = space();
    			if (if_block2) if_block2.c();
    			t2 = space();
    			div1 = element("div");
    			ul = element("ul");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			t3 = space();
    			create_component(infinitescroll.$$.fragment);
    			t4 = space();
    			p = element("p");
    			if_block3.c();
    			attr_dev(div0, "class", "col-md-auto");
    			add_location(div0, file$5, 223, 4, 5719);
    			attr_dev(ul, "class", "list-group my-1 svelte-1uhirki");
    			add_location(ul, file$5, 248, 6, 6390);
    			attr_dev(p, "class", "scroll-footer svelte-1uhirki");
    			add_location(p, file$5, 260, 6, 6722);
    			attr_dev(div1, "class", "col");
    			add_location(div1, file$5, 247, 4, 6366);
    			attr_dev(div2, "class", "row");
    			add_location(div2, file$5, 222, 2, 5697);
    			attr_dev(div3, "class", "container");
    			add_location(div3, file$5, 221, 0, 5671);
    		},
    		l: function claim(nodes) {
    			throw new Error_1("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div3, anchor);
    			append_dev(div3, div2);
    			append_dev(div2, div0);
    			if (if_block0) if_block0.m(div0, null);
    			append_dev(div0, t0);
    			if (if_block1) if_block1.m(div0, null);
    			append_dev(div0, t1);
    			if (if_block2) if_block2.m(div0, null);
    			append_dev(div2, t2);
    			append_dev(div2, div1);
    			append_dev(div1, ul);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(ul, null);
    			}

    			append_dev(ul, t3);
    			mount_component(infinitescroll, ul, null);
    			append_dev(div1, t4);
    			append_dev(div1, p);
    			if_block3.m(p, null);
    			current = true;
    		},
    		p: function update(ctx, dirty) {
    			if (show_if_2) if_block0.p(ctx, dirty);
    			if (show_if_1) if_block1.p(ctx, dirty);
    			if (show_if) if_block2.p(ctx, dirty);

    			if (dirty[0] & /*data, baseURL*/ 2049) {
    				each_value = /*data*/ ctx[0];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$2(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    						transition_in(each_blocks[i], 1);
    					} else {
    						each_blocks[i] = create_each_block$2(child_ctx);
    						each_blocks[i].c();
    						transition_in(each_blocks[i], 1);
    						each_blocks[i].m(ul, t3);
    					}
    				}

    				group_outros();

    				for (i = each_value.length; i < each_blocks.length; i += 1) {
    					out(i);
    				}

    				check_outros();
    			}

    			const infinitescroll_changes = {};

    			if (!updating_hasMore && dirty[0] & /*hasMore*/ 128) {
    				updating_hasMore = true;
    				infinitescroll_changes.hasMore = /*hasMore*/ ctx[7];
    				add_flush_callback(() => updating_hasMore = false);
    			}

    			infinitescroll.$set(infinitescroll_changes);

    			if (current_block_type === (current_block_type = select_block_type(ctx)) && if_block3) {
    				if_block3.p(ctx, dirty);
    			} else {
    				if_block3.d(1);
    				if_block3 = current_block_type(ctx);

    				if (if_block3) {
    					if_block3.c();
    					if_block3.m(p, null);
    				}
    			}
    		},
    		i: function intro(local) {
    			if (current) return;
    			transition_in(if_block0);
    			transition_in(if_block1);
    			transition_in(if_block2);

    			for (let i = 0; i < each_value.length; i += 1) {
    				transition_in(each_blocks[i]);
    			}

    			transition_in(infinitescroll.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(if_block0);
    			transition_out(if_block1);
    			transition_out(if_block2);
    			each_blocks = each_blocks.filter(Boolean);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				transition_out(each_blocks[i]);
    			}

    			transition_out(infinitescroll.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div3);
    			if (if_block0) if_block0.d();
    			if (if_block1) if_block1.d();
    			if (if_block2) if_block2.d();
    			destroy_each(each_blocks, detaching);
    			destroy_component(infinitescroll);
    			if_block3.d();
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$6.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function errorResponse(code, msg) {
    	return e => {
    		e.status = code;
    		e.details = msg;
    		throw e;
    	};
    }

    function ifEmpty(fn) {
    	return o => o || fn(new Error("empty"));
    }

    function instance$6($$self, $$props, $$invalidate) {
    	let $_;
    	validate_store(nn, "_");
    	component_subscribe($$self, nn, $$value => $$invalidate(10, $_ = $$value));
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots("App", slots, []);
    	c("en", en$2);
    	c("fr", fr$2);

    	v({
    		initialLocale: "fr",
    		initialLocale: M()
    	});

    	let baseURL = "";

    	// if the api (like in this example) just have a simple numeric pagination
    	let page = 1;

    	// but most likely, you'll have to store a token to fetch the next page
    	let nextUrl = null;

    	// tweets json response
    	let resTweets = "";

    	// categories json response
    	let resCategories = "";

    	let resTags = "";

    	// store all the data here.
    	let data = [];

    	// store the new batch of data here.
    	let newBatch = [];

    	// store categories there
    	let categories = [];

    	// store tags there
    	let tags = [];

    	// not categorized
    	let not_categorized = {
    		tag: $_("uncategorized"),
    		summary: $_("uncategorized_summary"),
    		taggit_tag: 0,
    		checked: true
    	};

    	let selected_categories = [];
    	let selected_tags = [];
    	let cat_query = "";
    	let tag_query = "";
    	const initialUrl = `${baseURL}/conversation/api/v1/tweets/?format=json&page=1`;
    	let hasMore = false;
    	let api_access;

    	/* DatePickr */
    	let from_datetime_query = "";

    	let to_datetime_query = "";

    	async function fetchDataTweets() {
    		let data_url = nextUrl == null ? initialUrl : nextUrl;

    		if (data_url == "null") {
    			return;
    		}

    		//console.log(`fetching: ${data_url}${cat_query}${tag_query}`)
    		const response = await fetch(`${data_url}${cat_query}${tag_query}${from_datetime_query}${to_datetime_query}`);

    		resTweets = await response.json();

    		//console.log(resTweets);
    		$$invalidate(27, newBatch = resTweets["results"]);

    		//console.log(newBatch);
    		nextUrl = resTweets["next"];

    		//console.log(`nextUrl: ${nextUrl}`);
    		$$invalidate(7, hasMore = nextUrl == null ? false : true);
    	}

    	

    	async function fetchDataCategories() {
    		const response = await fetch(`${baseURL}/tagging/api/v1/categories/`);

    		if (!response.ok) {
    			const message = `An error has occured: ${response.status}`;

    			//console.log(message);
    			//throw new Error(message);
    			return;
    		}

    		resCategories = await response.json();
    		$$invalidate(1, categories = resCategories["results"]);

    		for (var i = 0; i < categories.length; i++) {
    			$$invalidate(1, categories[i].checked = true, categories);
    			selected_categories.push(categories[i].taggit_tag);
    		}

    		categories.push(not_categorized);
    		selected_categories.push(not_categorized.taggit_tag);
    	}

    	

    	async function fetchDataTags() {
    		const response = await fetch(`${baseURL}/tagging/api/v1/tags/`);

    		if (!response.ok) {
    			const message = `An error has occured: ${response.status}`;

    			//console.log(message);
    			return;
    		} //throw new Error(message);

    		resTags = await response.json();
    		$$invalidate(2, tags = resTags["results"]);

    		for (var i = 0; i < tags.length; i++) {
    			$$invalidate(2, tags[i].checked = false, tags);
    			$$invalidate(2, tags[i]["taggit_tag"] = tags[i].tag.toString(), tags);
    			$$invalidate(2, tags[i]["tag"] = tags[i].tag_name, tags);
    		}
    	}

    	

    	async function fetchUserApiAccess() {
    		const response = await fetch(`${baseURL}/community/api/v1/user-api-access/`);

    		if (!response.ok) {
    			const message = `An error has occured: ${response.status}`;

    			//console.log(message);
    			return;
    		}

    		api_access = await response.json();
    		return api_access;
    	}

    	

    	function has_api_access(item) {
    		var access = fetchUserApiAccess;

    		//console.log(`access[item] == "true" ${access[item] == "true"}`)
    		return access[item] == "true";
    	}

    	onMount(() => {
    		// load first batch
    		fetchDataTweets();

    		// load categories
    		fetchDataCategories();

    		// load tags
    		fetchDataTags();
    	});

    	
    	
    	
    	
    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== "$$") console.warn(`<App> was created with unknown prop '${key}'`);
    	});

    	function categories_1_categories_binding(value) {
    		categories = value;
    		$$invalidate(1, categories);
    	}

    	function categories_1_selected_categories_binding(value) {
    		selected_categories = value;
    		$$invalidate(3, selected_categories);
    	}

    	function categories_1_query_binding(value) {
    		cat_query = value;
    		$$invalidate(5, cat_query);
    	}

    	function categories_1_selected_categories_binding_1(value) {
    		selected_tags = value;
    		$$invalidate(4, selected_tags);
    	}

    	function categories_1_query_binding_1(value) {
    		tag_query = value;
    		$$invalidate(6, tag_query);
    	}

    	function datepicker_from_datetime_query_binding(value) {
    		from_datetime_query = value;
    		$$invalidate(8, from_datetime_query);
    	}

    	function datepicker_to_datetime_query_binding(value) {
    		to_datetime_query = value;
    		$$invalidate(9, to_datetime_query);
    	}

    	function infinitescroll_hasMore_binding(value) {
    		hasMore = value;
    		$$invalidate(7, hasMore);
    	}

    	const loadMore_handler = () => {
    		fetchDataTweets();
    	};

    	$$self.$capture_state = () => ({
    		onMount,
    		addMessages: c,
    		init: v,
    		_: nn,
    		getLocaleFromNavigator: M,
    		InfiniteScroll,
    		Status,
    		Categories,
    		DatePicker,
    		en: en$2,
    		fr: fr$2,
    		baseURL,
    		page,
    		nextUrl,
    		resTweets,
    		resCategories,
    		resTags,
    		data,
    		newBatch,
    		categories,
    		tags,
    		not_categorized,
    		selected_categories,
    		selected_tags,
    		cat_query,
    		tag_query,
    		initialUrl,
    		hasMore,
    		api_access,
    		errorResponse,
    		ifEmpty,
    		from_datetime_query,
    		to_datetime_query,
    		fetchDataTweets,
    		fetchDataCategories,
    		fetchDataTags,
    		fetchUserApiAccess,
    		has_api_access,
    		$_
    	});

    	$$self.$inject_state = $$props => {
    		if ("baseURL" in $$props) $$invalidate(11, baseURL = $$props.baseURL);
    		if ("page" in $$props) page = $$props.page;
    		if ("nextUrl" in $$props) nextUrl = $$props.nextUrl;
    		if ("resTweets" in $$props) resTweets = $$props.resTweets;
    		if ("resCategories" in $$props) resCategories = $$props.resCategories;
    		if ("resTags" in $$props) resTags = $$props.resTags;
    		if ("data" in $$props) $$invalidate(0, data = $$props.data);
    		if ("newBatch" in $$props) $$invalidate(27, newBatch = $$props.newBatch);
    		if ("categories" in $$props) $$invalidate(1, categories = $$props.categories);
    		if ("tags" in $$props) $$invalidate(2, tags = $$props.tags);
    		if ("not_categorized" in $$props) not_categorized = $$props.not_categorized;
    		if ("selected_categories" in $$props) $$invalidate(3, selected_categories = $$props.selected_categories);
    		if ("selected_tags" in $$props) $$invalidate(4, selected_tags = $$props.selected_tags);
    		if ("cat_query" in $$props) $$invalidate(5, cat_query = $$props.cat_query);
    		if ("tag_query" in $$props) $$invalidate(6, tag_query = $$props.tag_query);
    		if ("hasMore" in $$props) $$invalidate(7, hasMore = $$props.hasMore);
    		if ("api_access" in $$props) api_access = $$props.api_access;
    		if ("from_datetime_query" in $$props) $$invalidate(8, from_datetime_query = $$props.from_datetime_query);
    		if ("to_datetime_query" in $$props) $$invalidate(9, to_datetime_query = $$props.to_datetime_query);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty[0] & /*cat_query*/ 32) {
    			 if (cat_query.length > 0) {
    				$$invalidate(0, data = []);
    				$$invalidate(27, newBatch = []);
    				nextUrl = null;
    				fetchDataTweets();
    			}
    		}

    		if ($$self.$$.dirty[0] & /*tag_query*/ 64) {
    			 if (tag_query.length >= 0) {
    				$$invalidate(0, data = []);
    				$$invalidate(27, newBatch = []);
    				nextUrl = null;
    				fetchDataTweets();
    			}
    		}

    		if ($$self.$$.dirty[0] & /*from_datetime_query*/ 256) {
    			 if (from_datetime_query.length > 0) {
    				$$invalidate(0, data = []);
    				$$invalidate(27, newBatch = []);
    				nextUrl = null;
    				fetchDataTweets();
    			}
    		}

    		if ($$self.$$.dirty[0] & /*to_datetime_query*/ 512) {
    			 if (to_datetime_query.length > 0) {
    				$$invalidate(0, data = []);
    				$$invalidate(27, newBatch = []);
    				nextUrl = null;
    				fetchDataTweets();
    			}
    		}

    		if ($$self.$$.dirty[0] & /*data, newBatch*/ 134217729) {
    			 $$invalidate(0, data = [...data, ...newBatch]);
    		}
    	};

    	return [
    		data,
    		categories,
    		tags,
    		selected_categories,
    		selected_tags,
    		cat_query,
    		tag_query,
    		hasMore,
    		from_datetime_query,
    		to_datetime_query,
    		$_,
    		baseURL,
    		fetchDataTweets,
    		has_api_access,
    		categories_1_categories_binding,
    		categories_1_selected_categories_binding,
    		categories_1_query_binding,
    		categories_1_selected_categories_binding_1,
    		categories_1_query_binding_1,
    		datepicker_from_datetime_query_binding,
    		datepicker_to_datetime_query_binding,
    		infinitescroll_hasMore_binding,
    		loadMore_handler
    	];
    }

    class App extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$6, create_fragment$6, safe_not_equal, {}, [-1, -1]);

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "App",
    			options,
    			id: create_fragment$6.name
    		});
    	}
    }

    var app = new App({
    	target: document.body
    });

    return app;

}());
//# sourceMappingURL=bundle.js.map
