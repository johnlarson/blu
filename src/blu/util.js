import { createElement as $ } from 'https://esm.sh/react';
import { createRoot } from 'https://esm.sh/react-dom/client';

console.log('Hello from client utils!');

export function render_root(py_root) {
  const jsNode = getReactNode(py_root);
  const jsRoot = isValidRootNode(jsNode) ? jsNode : $('div', null, jsNode);
  const renderTarget = jsRoot.type == 'html' ? document : document.body;
  createRoot(renderTarget).render(jsRoot);
}

function getReactNode(pyNode) {

}

export function use_state(init) {

}

export function use_ref(init) {

}

export function use_effect(callback) {

}