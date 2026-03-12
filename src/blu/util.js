import react from 'https://esm.sh/react';
import { createElement as $, Fragment } from 'https://esm.sh/react';
import { createRoot } from 'https://esm.sh/react-dom/client';
import * as PyScript from 'https://pyscript.net/releases/2026.1.1/core.js';

window.ps = PyScript;

console.log('Hello from client utils!');
console.log('PYSCRIPT INTERPRETER:', PyScript)

let createProxy;
let blu;
let builtins;
let abc;

export function init(innerPyImport) {
  const ffi = innerPyImport('pyscript.ffi');
  createProxy = ffi.create_proxy(ffi.create_proxy);
  function pyImport(location) {
    return createProxy(innerPyImport(location))
  }
  blu = pyImport('blu');
  builtins = pyImport('builtins');
  abc = pyImport('collections.abc')
}

export function renderRoot(pyRootIn) {
  const pyRoot = createProxy(pyRootIn);
  const jsNode = getReactNode(pyRoot);
  const renderTarget = jsNode.type === 'html' ? document : document.body;
  createRoot(renderTarget).render(jsNode);
}

function getReactNode(pyNode) {
  if (isOfType(pyNode, blu.ClientElement)) {
    return $(PythonElement, {
      renderer: pyNode._renderer,
      args: pyNode._args,
      kwargs: pyNode._kwargs,
      pyChildren: pyNode._children,
    })
  } else if (isOfType(pyNode, blu.Key)) {
    return $(Fragment, { key: pyNode._key },
      ...getArray(pyNode._children),
    );
  } else if (isOfType(pyNode, builtins.tuple)) {
    return $(Fragment, null, ...getArray(pyNode));
  } else if (typeof pyNode === 'string') {
    return pyNode;
  } else if (isOfType(pyNode, abc.Iterable)) {
    return getArray(pyNode);
  } else if (isOfType(pyNode, blu.HTMLElement)) {
    // TODO: Figure out how to deal with props and ref
    const attrs = {};
    let hasRef = false;
    for (const [k, v] of pyNode._attrs.items()) {
      if (k == 'ref') {
        hasRef = true;
        continue;
      }
      attrs[k] = v;
    }
    if (hasRef) {
      attrs['ref'] = pyNode._attrs['ref']._ref_proxy;
    }
    return $(pyNode._tagname, attrs, ...getArray(pyNode._children));
  } else if (pyNode === undefined) {
    return undefined;
  } else {
    return pyNode.toString();
  }
}

function PythonElement({ renderer, args, kwargs, pyChildren }) {
  react.useEffect(() => () => {
    retProxy.destroy();
  })
  const result = renderer.callKwargs(...args, kwargs);
  let pyNode;
  if (isinstance(result, abc.Generator)) {
    result.next();
    pyNode = result.return(pyChildren).value;
  } else {
    pyNode = result;
  }
  let retProxy = createProxy(pyNode);
  return getReactNode(retProxy);
}

function getArray(pyIterable) {
  return Array.from(pyIterable).map(x => getReactNode(x));
}

export function useState(init) {
  const notMemoryManaged = ['number', 'string', 'boolean'].includes(typeof init) ||
                           [undefined, null].includes(init);
  const wrapped = notMemoryManaged ? init : createProxy(init);
  react.useEffect(() => () => {
    if (!notMemoryManaged) {
      ret.destroy();
    }
  });
  return react.useState(wrapped);
}

export function useRefObj(pyRef) {
  const refProxiedRef = react.useRef(false);
  if (!refProxiedRef.current) {
    pyRef = createProxy(pyRef);
    refProxiedRef.current = true;
    pyRef._ref_proxy = refProxy();
  }
  const refRef = useRef(pyRef);
  react.useEffect(() => () => {
    refRef.current.destroy();
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
  react.useEffect(() => {
    const result = callback();
    if (isinstance(result, abc.Generator)) {
      const generator = createProxy(result);
      return () => {
        generator.next();
        generator.destroy();
      };
    }
  })
}

function isOfType(obj, pyClass) {
  if (!pyClass.match(/^<class '[_A-Za-z0-9\.]+'>$/g)) {
    throw Error('Second argument must be a Python class.')
  }
  return obj.__class__.toString() === pyClass.toString();
}