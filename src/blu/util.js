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

export function init(innerPyImport) {
  const ffi = innerPyImport('pyscript.ffi');
  create_proxy = ffi.create_proxy(ffi.create_proxy);
  function pyImport(location) {
    return create_proxy(innerPyImport(location))
  }
  blu = pyImport('blu');
  builtins = pyImport('builtins');
  abc = pyImport('collections.abc')
}

const idToProxy = new Map()
const proxyToId = new Map()

const PRIMITIVE_TYPES = ['undefined', 'boolean', 'number', 'bigint', 'string', 'symbol'];

function getProxy(obj) {
  if (obj === null || PRIMITIVE_TYPES.includes(typeof obj)) {
    return obj;
  }
  const id = builtins.id(obj);
  if (!idToProxy.has(id)) {
    const proxy = create_proxy(obj)
    idToProxy.set(id, proxy);
    proxyToId.set(proxy, id);
  }
  return idToProxy.get(id);
}

function destroy(pyProxy) {
  if (pyProxy === null || PRIMITIVE_TYPES.includes(typeof pyObj)) {
    return;
  }
  const id = proxyToId(pyProxy);
  proxyToId.delete(pyProxy);
  idToProxy.delete(id);
  pyProxy.destroy();
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
      pyChildren: getProxy(pyNode._children),
    })
  } else if (isOfType(pyNode, blu.Key)) {
    return $(MemManagedFragment, {
      key: getProxy(pyNode._key), children: getProxy(pyNode._children)
    });
  } else if (isOfType(pyNode, builtins.tuple)) {
    return $(MemManagedFragment, { children: getProxy(pyNode._children) });
  } else if (typeof pyNode === 'string') {
    return pyNode;
  } else if (isOfType(pyNode, abc.Iterable)) {
    return $(MemManagedIterable, { children: getProxy(pyNode._children) });
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
    return $(MemManagedHTMLElement, {
      _blu_tagname: pyNode._tagname, children: getProxy(pyNode._children), ...attrs
    });
  } else if (pyNode === undefined) {
    return undefined;
  } else {
    return pyNode.toString();
  }
}

function PythonElement({ renderer, args, kwargs, pyChildren }) {
  React.useEffect(() => () => {
    destroy(renderer);
    destroy(args);
    destroy(kwargs);
    destroy(pyChildren);
  }, []);
  const result = renderer.callKwargs(...args, kwargs.toJs({ depth: 1 }));
  let pyNode;
  if (builtins.isinstance(result, abc.Generator)) {
    result.next();
    pyNode = result.return(pyChildren).value;
  } else {
    pyNode = result;
  }
  return getReactNode(pyNode);
}

function MemManagedFragment({ key, children }) {
  React.useEffect(() => () => {
    destroy(key);
    destroy(children);
  }, []);
  return $(React.Fragment, { key }, ...getArray(children));
}

function MemManagedIterable({ children }) {
  React.useEffect(() => () => {
    destroy(children);
  }, []);
  return getArray(children);
}

function MemManagedHTMLElement({ _blu_tagname, children, ...attrs }) {
  React.useEffect(() => () => {
    destroy(children);
    for (const attr_value of Object.values(attrs)) {
      destroy(attr_value);
    }
  }, []);
  return $(_blu_tagname, attrs, ...getArray(children));
}

function getArray(pyIterable) {
  if (pyIterable === undefined) {
    return [];
  }
  const ret = [];
  for (const item of pyIterable) {
    ret.push(getReactNode(item));
  }
  return ret;
}

export function useState(init) {
  const notMemoryManaged = ['number', 'string', 'boolean'].includes(typeof init) ||
                           [undefined, null].includes(init);
  const wrapped = notMemoryManaged ? init : getProxy(init);
  React.useEffect(() => () => {
    if (!notMemoryManaged) {
      destroy(ret);
    }
  });
  return React.useState(wrapped);
}

export function useRefObj(pyRef) {
  const refProxiedRef = React.useRef(false);
  if (!refProxiedRef.current) {
    pyRef = getProxy(pyRef);
    refProxiedRef.current = true;
    pyRef._ref_proxy = refProxy();
  }
  const refRef = useRef(pyRef);
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
  React.useEffect(() => {
    const result = callback();
    if (isinstance(result, abc.Generator)) {
      const generator = createProxy(result);
      return () => {
        generator.next();
        destroy(generator);
      };
    }
  })
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