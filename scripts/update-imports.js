const path = require('path');

module.exports = function transformer(fileInfo, api, options) {
    const j = api.jscodeshift;
    const root = j(fileInfo.source);

    const { oldPath, newPath } = options;

    function isImportingFile(importPath, sourceFilePath, targetFilePath) {
        if (!importPath.startsWith('.')) {
            return false;
        }
        const sourceDir = path.dirname(sourceFilePath);
        const resolvedImport = path.resolve(sourceDir, importPath);
        const resolvedTarget = path.resolve(targetFilePath);
        return resolvedImport.replace(/\.(ts|tsx|js|jsx)$/, '') ===
            resolvedTarget.replace(/\.(ts|tsx|js|jsx)$/, '');
    }

    root.find(j.ImportDeclaration)
        .filter(p => {
            const importSource = p.node.source.value;
            return isImportingFile(importSource, fileInfo.path, oldPath);
        })
        .forEach(p => {
            const sourceDir = path.dirname(fileInfo.path);
            let newRelativePath = path.relative(sourceDir, newPath);
            if (!newRelativePath.startsWith('..')) {
                newRelativePath = './' + newRelativePath;
            }
            newRelativePath = newRelativePath.replace(/\.(ts|tsx|js|jsx)$/, '');
            j(p).find(j.Literal).replaceWith(j.literal(newRelativePath));
        });

    return root.toSource();
};
