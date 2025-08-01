import { readFileSync } from 'fs';

/**
 * Transform TypeScript import paths based on mapping from file_map.json.
 * Usage: jscodeshift -t scripts/refactor/update_ts_imports.js <paths> --map path/to/file_map.json
 */
export default function transformer(fileInfo, api, options) {
  const j = api.jscodeshift;
  const mappingPath = options.map || 'file_map.json';
  const raw = JSON.parse(readFileSync(mappingPath, 'utf8'));

  const aliasMap = buildAliasMap(raw);

  const root = j(fileInfo.source);

  root.find(j.ImportDeclaration).forEach(p => {
    const source = p.node.source.value;
    if (typeof source !== 'string') {
      return;
    }
    const updated = rewritePath(source, aliasMap);
    if (updated && updated !== source) {
      p.node.source.value = updated;
    }
  });

  return root.toSource({ quote: 'single' });

  function buildAliasMap(map) {
    const out = {};
    for (const [oldFile, newFile] of Object.entries(map)) {
      if (oldFile.startsWith('frontend/src/') && newFile.startsWith('src/frontend/react_app/src/')) {
        const relOld = oldFile.replace(/^frontend\/src\//, '');
        const relNew = newFile.replace(/^src\/frontend\/react_app\/src\//, '');
        const oldAlias = '@/' + relOld.replace(/\.[tj]sx?$/, '');
        const newAlias = '@/' + relNew.replace(/\.[tj]sx?$/, '');
        out[oldAlias] = newAlias;            // alias -> alias (for files already using @/)
        out[oldFile.replace(/\.[tj]sx?$/, '')] = newAlias;  // raw path -> alias
      }
    }
    return out;
  }

// sourcery skip: avoid-function-declarations-in-blocks
  function rewritePath(value, map) {
    if (map[value]) {
      return map[value];
    }
    for (const key of Object.keys(map)) {
      if (value.startsWith(key + '/')) {
        return map[key] + value.slice(key.length);
      }
    }
    return null;
  }
};
