import * as mp_mjs from '/_blu_internal/static/micropython.mjs'
import * as zipJs from 'https://cdn.jsdelivr.net/npm/@zip.js/zip.js@2.11.4/+esm';
import * as react from 'https://esm.sh/react';
import * as reactDom from 'https://esm.sh/react-dom/client';

const mp = await mp_mjs.loadMicroPython();



async function addPackage(url, dest) {
  const appZipResponse = await fetch(url);
  const appZipContent = await appZipResponse.blob();
  const zipFileReader = new zipJs.BlobReader(appZipContent);
  const zipReader = new zipJs.ZipReader(zipFileReader);
  mp.FS.mkdir(dest)
  for (const entry of await zipReader.getEntries()) {
    const fullPath = `${dest}/${entry.filename}`;
    //console.log(entry);
    if (entry.directory) {
      //mp.FS.mkdir(fullPath);
    } else {
      const fArrayBuff = await entry.arrayBuffer();
      const text = new TextDecoder().decode(fArrayBuff);
      // console.log("text:", text);
      const dir = fullPath.split('/').slice(0, -1).join('/');
      mp.FS.mkdirTree(dir);
      mp.FS.writeFile(fullPath, fArrayBuff);
    }
  }
  await zipReader.close();
}

const PACKAGE_INDEX_ROOT = 'https://micropython.org/pi/v2'

async function mpInstall(packageName) {
  const metadataUrl = `${PACKAGE_INDEX_ROOT}/package/py/${packageName}/latest.json`;
  const metadata = await (await fetch(metadataUrl)).json();
  for (const [name, hash] of metadata.hashes) {
    const fileUrl = `${PACKAGE_INDEX_ROOT}/file/${hash.slice(0, 2)}/${hash}`;
    const content = await (await fetch(fileUrl)).arrayBuffer();
    const fullPath = `/${name}`;
    const dir = fullPath.split('/').slice(0, -1).join('/');
    mp.FS.mkdirTree(dir);
    mp.FS.writeFile(fullPath, content);
  }

}

await addPackage('/_blu_internal/app_pkg.zip', '/app');
await addPackage('/_blu_internal/blu_pkg.zip', '/blu');
await mpInstall('pathlib');
await mpInstall('functools');
await mpInstall('inspect');
await mpInstall('logging');
await mpInstall('base64');
await mpInstall('types');
await mpInstall('contextlib');
mp.registerJsModule('_react', react);
mp.registerJsModule('_react_dom', reactDom);



// const pyUtils = mp.pyimport('blu._utils');
// const pyRoot = pyUtils.unpickle_root();
// console.log(pyRoot);

// const blu = mp.pyimport('blu');
// const builtins = mp.pyimport('builtins');
// const isinstance = builtins.isinstance

// const jsNode = getReactNode(pyRoot);
// const renderTarget = jsNode.type === 'html' ? document : document.body;
// reactDom.createRoot(renderTarget).render(jsNode);


await mp.pyimport('blu._client_main').main();


function isOfType(obj, pyClass) {
  return builtins.id(builtins.type(obj)) === builtins.id(pyClass)
}

function getReactNode(pyNode) {
  console.log('ISINSTANCE:', isinstance(pyNode, blu.ClientElement))
  if (isOfType(pyNode, blu.ClientElement)) {
    return $(PythonElement, {
        renderer: getProxy(pyNode._renderer),
        args: getProxy(pyNode._args),
        kwargs: getProxy(pyNode._kwargs),
        pyChildren: getProxy(pyNode._children)
    })
  } else if (isOfType(pyNode, blu.Key)) {
    return $(MemManagedFragment, { key: getProxy(pyNode._key) }, ...getArray(pyNode._children));
  } else if (isOfType(pyNode, builtins.tuple)) {
    return $(React.Fragment, null, ...getArray(pyNode));
  } else if (typeof pyNode === 'string') {
    return pyNode;
  } else if (builtins.hasattr(pyNode, '__iter__')) {
    return getArray(pyNode);
  } else if (isOfType(pyNode, blu.HTMLElement)) {
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
      attrs['ref'] = pyNode._attrs['ref']._ref_proxy;
    }
    return $(MemManagedHTMLElement, { _blu_tagname: pyNode._tagname, ...attrs },
      ...getArray(pyNode._children),
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
  const { renderer, args, kwargs, pyChildren } = unwrapProxyProps(proxies);
  const result = renderer.callKwargs(...args, kwargs.toJs({ depth: 1 }));
  let pyNode;
  if (isGenerator(result)) {
    result.next();
    try {
      if (pyChildren.length === 1) {
        result.send(pyChildren[0]);
      } else {
        result.send(pyChildren);
      }
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
  const childrenArray = getChildrenArray(children);
  React.useEffect(() => () => {
    destroy(key);
  }, []);
  return $(React.Fragment, { key }, ...childrenArray);
}

function getChildrenArray(children) {
  return children instanceof Array ? children : [children];
}

function unwrapChildren(children) {
  if (children instanceof Array) {
    return children.map(x => unwrap(x));
  } else {
    return unwrap(children);
  }
}

function destroyChildren(children) {
  if (children instanceof Array) {
    for (const child of children) {
      destroy(child);
    }
  } else {
    destroy(children);
  }
}

function MemManagedHTMLElement({ _blu_tagname, children, ...attrs }) {
  const childrenArray = getChildrenArray(children);
  React.useEffect(() => () => {
    for (const attr_value of Object.values(attrs)) {
      destroy(attr_value);
    }
  }, []);
  return $(_blu_tagname, attrs, ...childrenArray);
}

function childrenReactArray(children) {
  const childrenArray = children instanceof Array ? children : [children];
  return childrenArray.map(x => getReactNode(x));
}

function getArray(pyIterable) {
  pyIterable = unwrap(pyIterable);
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
    const packed = useEffectInvoke(callbackProxy);
    const tag = operator.getitem(packed, 0).toString();
    const result = operator.getitem(packed, 1);
    if (tag === 'async_generator') {
      const agen = getProxy(result);
      return () => {
        const onDone = create_proxy(() => {
          destroy(agen);
          onDone.destroy();
        });
        useEffectCleanupAsyncGen(agen, onDone);
        destroy(callbackProxy);
      };
    } else if (tag === 'coroutine') {
      const coro = getProxy(result);
      return () => {
        try {
          coro.close();
        } catch (e) {
          // ignore close errors during unmount
        }
        destroy(coro);
        destroy(callbackProxy);
      };
    } else if (tag === 'generator') {
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
      };
    }
  });
}

// function isOfType(obj, pyClass) {
//   if (pyClass === undefined || !pyClass.toString().match(/^<class '[_A-Za-z0-9\.]+'>$/g)) {
//     throw Error('Second argument must be a Python class.')
//   }
//   if (obj?.__class__ === undefined) {
//     return false;
//   }
//   return obj.__class__.toString() === pyClass.toString();
// }

function pyIs(obj1, obj2) {
  return obj1.__repr__() === obj2.__repr__()
}