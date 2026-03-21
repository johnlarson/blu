import React from 'https://esm.sh/react';
import { createElement as $, Fragment } from 'https://esm.sh/react';
import { createRoot } from 'https://esm.sh/react-dom/client';
import * as PyScript from 'https://pyscript.net/releases/2026.1.1/core.js';

window.ps = PyScript;

console.log('Hello from client utils!');
console.log('PYSCRIPT INTERPRETER:', PyScript)

let create_proxy;
let blu;
let builtins;
let abc;
let sys;
let renderClientElement;

export function init(innerPyImport) {
  const ffi = innerPyImport('pyscript.ffi');
  create_proxy = ffi.create_proxy(ffi.create_proxy);
  function pyImport(location) {
    return create_proxy(innerPyImport(location))
  }
  blu = pyImport('blu');
  builtins = pyImport('builtins');
  abc = pyImport('collections.abc');
  sys = pyImport('sys');
  renderClientElement = pyImport('blu._nodes')._render_client_element
}

const idToProxyInfo = new Map();
const proxyToId = new Map();

const PRIMITIVE_TYPES = ['undefined', 'boolean', 'number', 'bigint', 'string', 'symbol'];

function getProxy(obj) {
  if (obj === null || PRIMITIVE_TYPES.includes(typeof obj)) {
    return obj;
  }
  const id = builtins.id(obj);
  if (!idToProxyInfo.has(id)) {
    const proxy = create_proxy(obj)
    idToProxyInfo.set(id, {
      proxy,
      count: 0
    });
    proxyToId.set(proxy, id);
  }
  const proxyInfo = idToProxyInfo.get(id);
  proxyInfo.count++;
  return proxyInfo.proxy;
}

function destroy(pyProxy) {
  if (pyProxy === null || PRIMITIVE_TYPES.includes(typeof pyObj)) {
    return;
  }
  const id = proxyToId(pyProxy);
  const proxyInfo = idToProxyInfo(id);
  const { proxy, count } = proxyInfo;
  if (count < 1) {
    throw new Error(`Too few existing copies (${count}) when destroying ${proxy}`);
  }
  proxyInfo.count--;
  if (proxyInfo.count === 0) {
    proxyToId.delete(proxy);
    idToProxyInfo.delete(id);
    proxy.destroy();
  }
}

function unwrap(thing) {
  if ([undefined, null].includes(thing)) {
    return thing;
  }
  while (thing.type === 'pyodide.ffi.JsProxy') {
    thing = thing.unwrap();
  }
  return thing;
}

export function renderRoot(pyRoot) {
  const jsNode = getReactNode(pyRoot);
  const renderTarget = jsNode.type === 'html' ? document : document.body;
  createRoot(renderTarget).render(jsNode);
}

function getReactNode(pyNode) {
  if (isOfType(pyNode, blu.ClientElement)) {
    return $(PythonElement, {
        renderer: getProxy(pyNode._renderer),
        args: getProxy(pyNode._args),
        kwargs: getProxy(pyNode._kwargs),
      },
      ...getProxies(pyNode._children),
    )
  } else if (isOfType(pyNode, blu.Key)) {
    return $(MemManagedFragment, { key: getProxy(pyNode._key) }, ...getProxies(pyNode._children));
  } else if (isOfType(pyNode, builtins.tuple)) {
    return $(MemManagedFragment, null, ...getProxies(pyNode));
  } else if (typeof pyNode === 'string') {
    return pyNode;
  } else if (builtins.hasattr(pyNode, '__iter__')) {
    return $(MemManagedIterable, null, ...getProxies(pyNode));
  } else if (isOfType(pyNode, blu.HTMLElement)) {
    // TODO: Figure out how to deal with props and ref
    const attrs = {};
    let hasRef = false;
    for (const [k, v] of pyNode._attrs.items()) {
      if (k == 'ref') {
        hasRef = true;
        continue;
      }
      attrs[k] = getProxy(v);
    }
    if (hasRef) {
      attrs['ref'] = getProxy(pyNode._attrs['ref']._ref_proxy);
    }
    return $(MemManagedHTMLElement, { _blu_tagname: pyNode._tagname, ...attrs },
      ...getProxies(pyNode._children),
    );
  } else if (pyNode === undefined) {
    return undefined;
  } else {
    return pyNode.toString();
  }
}

function getProxies(items) {
  const ret = [];
  for (const item of items) {
    ret.push(getProxy(item));
  }
  return ret
}

function PythonElement(proxies) {
  React.useEffect(() => () => {
    destroy(proxies.renderer);
    destroy(proxies.args);
    destroy(proxies.kwargs);
    destroy(proxies.pyChildren);
  }, []);
  // const pyNode = renderClientElement(props)
  const { renderer, args, kwargs, children } = unwrapProxyProps(proxies);
  if (children instanceof Array) {
    children = builtins.tuple(children);
  }
  const result = renderer.callKwargs(...args, kwargs.toJs({ depth: 1 }));
  let pyNode;
  if (builtins.isinstance(result, abc.Generator)) {
    result.next();
    try {
      result.send(children);
      // result.send([])
    } catch(e) {
      if (e.name === 'PythonError') {
        const pyExc = sys.last_exc;
        if (isOfType(pyExc, builtins.StopIteration)) {
          pyNode = pyExc.value;
        } else {
          throw e;
        }
      } else {
        throw e;
      }
    }
  } else {
    pyNode = result;
  }
  return getReactNode(pyNode);
}

function unwrapProxyProps(proxies) {
  const ret = {}
  for (const [k, v] of Object.entries(proxies)) {
    ret[k] = unwrap(v);
  }
  return ret
}

function MemManagedFragment({ key, children }) {
  children = unwrap(children);
  React.useEffect(() => () => {
    destroy(key);
    destroy(children);
  }, []);
  return $(React.Fragment, { key }, getReactNode(children));
}

function MemManagedIterable({ children }) {
  children = unwrap(children);
  React.useEffect(() => () => {
    destroy(children);
  }, []);
  return getArray(children);
}

function MemManagedHTMLElement({ _blu_tagname, children, ...attrs }) {
  children = unwrap(children);
  React.useEffect(() => () => {
    destroy(children);
    for (const attr_value of Object.values(attrs)) {
      destroy(attr_value);
    }
  }, []);
  return $(_blu_tagname, attrs, getReactNode(children));
}

function getArray(pyIterable) {
  pyIterable = unwrap(pyIterable);
  // if (pyIterable === undefined) {
  //   return [];
  // }
  const ret = [];
  for (const item of pyIterable) {
    ret.push(getReactNode(item));
  }
  return ret;
}

export function useState(init) {
  const initUsedRef = React.useRef(false);
  const wrapped = getProxy(init);
  const valueRef = React.useRef(wrapped);
  React.useEffect(() => () => {
    destroy(valueRef.current);
  });
  const [value, setValue] = React.useState(wrapped);
  if (initUsedRef.current) {
    destroy(wrapped);
  }
  initUsedRef.current = true;
  function setter(newValue) {
    destroy(valueRef.current);
    const newProxy = getProxy(newValue);
    valueRef.current = newProxy;
    setValue(newProxy);
  }
  return [value, setter];
}

export function useRefObj(pyRef) {
  const refProxiedRef = React.useRef(false);
  pyRef = getProxy(pyRef);
  pyRef._ref_proxy = refProxy(pyRef);
  const refRef = React.useRef(pyRef);
  if (refProxiedRef.current) {
    destroy(pyRef);
  }
  refProxiedRef.current = true;
  React.useEffect(() => () => {
    destroy(refRef.current);
  }, []);
  return refRef.current;
}

function refProxy(pyRef) {
  return {
    set current(newValue) {
      pyRef._value = newValue;
    }
  }
}

export function useEffect(callback) {
  const callbackProxy = getProxy(callback);
  React.useEffect(() => {
    const result = callbackProxy();
    if (builtins.isinstance(result, abc.Generator)) {
      const generator = getProxy(result);
      generator.next();
      return () => {
        generator.next();
        destroy(generator);
        destroy(callbackProxy);
      };
    } else {
      return () => {
        destroy(callbackProxy);
      }
    }
  });
}

function isOfType(obj, pyClass) {
  if (pyClass === undefined || !pyClass.toString().match(/^<class '[_A-Za-z0-9\.]+'>$/g)) {
    throw Error('Second argument must be a Python class.')
  }
  if (obj?.__class__ === undefined) {
    return false;
  }
  return obj.__class__.toString() === pyClass.toString();
}

function pyIs(obj1, obj2) {
  return obj1.__repr__() === obj2.__repr__()
}