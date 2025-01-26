bluget = (() => {

  const dependencyMapElement = document.querySelector('script[type="dependency-map"]');
  const dependencyMap = dependencyMapElement ? JSON.parse(dependencyMapElement.textContent) : null;

  async function bluget(moduleName) {
    const importName = moduleName.endsWith('.js') ? moduleName : `${moduleName}.js`;
    if (dependencyMap === null) {
      return await import(importName)
    }
    const dependencies = flattenDependencies(importName);
    console.log('DEPS:', dependencies)
    const dependencyPromises = dependencies.map(x => import(x));
    const modules = await Promise.all([import(importName), ...dependencyPromises]);
    return modules[0];
  }

  function flattenDependencies(moduleName) {
    return Array.from(flattenDependenciesRec(moduleName));
  }

  function flattenDependenciesRec(moduleName) {
    const immediateDeps = dependencyMap[moduleName] || [];
    let dependencies = new Set(immediateDeps);
    for (const dep of immediateDeps) {
      dependencies = [...dependencies, ...flattenDependenciesRec(dep)];
    }
    return dependencies;
  }

  return bluget;

})();