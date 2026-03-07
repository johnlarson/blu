import { createElement as $ } from 'https://esm.sh/react';
import { createRoot } from 'https://esm.sh/react-dom/client';
import PyScript from 'https://pyscript.net/releases/2026.1.1/core.js';

window.ps = PyScript;

console.log('Hello from client utils!');
console.log('PYSCRIPT INTERPRETER:', PyScript)

let create_proxy;
let blu;
let builtins;
let isinstance;

export function init(py_import) {
  const ffi = py_import('pyscript.ffi');
  create_proxy = ffi.create_proxy(ffi.create_proxy);
  blu = py_import('blu');
  builtins = py_import('builtins');
  isinstance = builtins.isinstance;
}

export function render_root(py_root) {
  const jsNode = getReactNode(py_root);
  const renderTarget = jsRoot.type === 'html' ? document : document.body;
  createRoot(renderTarget).render(jsNode);
}

function getReactNode(pyNode) {
  if (isinstance(pyNode, blu.ClientElement)) {
    return $(PythonElement, {
      renderer: create_proxy(pyNode._renderer),
      args: create_proxy(pyNode._args),
      kwargs: create_proxy(pyNode._kwargs),
    })
  } else if (isinstance(pyNode, blu.Key)) {

  } else if (isinstance(pyNode, builtins.tuple)) {

  } else if (typeof pyNode === 'string') {
    return pyNode;
  } else if (Symbol.iterator in pyNode) {

  } else if (isinstance(pyNode, blu.HTMLElement)) {

  } else if (pyNode === undefined) {
    return undefined;
  } else {
    return pyNode.toString();
  }
}

function PythonElement({}) {

}

export function use_state(init) {

}

export function use_ref(init) {

}

export function use_effect(callback) {

}