import react from 'https://esm.sh/react';
import { createElement as $, Fragment } from 'https://esm.sh/react';
import { createRoot } from 'https://esm.sh/react-dom/client';
import PyScript from 'https://pyscript.net/releases/2026.1.1/core.js';

window.ps = PyScript;

console.log('Hello from client utils!');
console.log('PYSCRIPT INTERPRETER:', PyScript)

let createProxy;
let blu;
let builtins;
let isinstance;
let abc;

export function init(innerPyImport) {
  const ffi = innerPyImport('pyscript.ffi');
  createProxy = ffi.create_proxy(ffi.create_proxy);
  function pyImport(location) {
    return createProxy(innerPyImport(location))
  }
  blu = pyImport('blu');
  builtins = pyImport('builtins');
  isinstance = builtins.isinstance;
  abc = pyImport('collections.abc')
}

export function renderRoot(pyRootIn) {
  const pyRoot = createProxy(pyRootIn);
  const jsNode = getReactNode(pyRoot);
  const renderTarget = jsNode.type === 'html' ? document : document.body;
  createRoot(renderTarget).render(jsNode);
}

function getReactNode(pyNode) {
  if (isinstance(pyNode, blu.ClientElement)) {
    return $(PythonElement, {
      renderer: pyNode._renderer,
      args: pyNode._args,
      kwargs: pyNode._kwargs,
      pyChildren: pyNode._children,
    })
  } else if (isinstance(pyNode, blu.Key)) {
    return $(Fragment, { key: pyNode._key },
      ...getArray(pyNode._children),
    );
  } else if (isinstance(pyNode, builtins.tuple)) {
    return $(Fragment, null, ...getArray(pyNode));
  } else if (typeof pyNode === 'string') {
    return pyNode;
  } else if (Symbol.iterator in pyNode) {
    return getArray(pyNode);
  } else if (isinstance(pyNode, blu.HTMLElement)) {
    return $(pyNode._tagname, null, ...getArray(pyNode._children));
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
  retProxy = createProxy(pyNode);
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
  
}

function useMemoryManagement(toManage, longLived = false) {
  const notMemoryManaged = ['number', 'string', 'boolean'].includes(typeof toManage) ||
                           [undefined, null].includes(toManage);
  const ret = notMemoryManaged ? toManage : createProxy(toManage);
  react.useEffect(() => () => {
    if (!notMemoryManaged) {
      ret.destroy();
    }
  });
  return ret;
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