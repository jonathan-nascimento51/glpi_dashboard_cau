import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

export default function (plop) {
  const root = dirname(fileURLToPath(import.meta.url));
  const tmpl = (file) => join(root, 'templates', file);

  plop.setGenerator('react-component', {
    description: 'Create a React component',
    prompts: [
      { type: 'input', name: 'name', message: 'Component name:' }
    ],
    actions: [
      {
        type: 'add',
        path: 'src/frontend/react_app/src/components/{{pascalCase name}}/{{pascalCase name}}.tsx',
        templateFile: tmpl('react-component/component.tsx.hbs')
      },
      {
        type: 'add',
        path: 'src/frontend/react_app/src/components/{{pascalCase name}}/{{camelCase name}}.module.css',
        templateFile: tmpl('react-component/component.module.css.hbs')
      },
      {
        type: 'add',
        path: 'src/frontend/react_app/src/components/{{pascalCase name}}/index.ts',
        templateFile: tmpl('react-component/index.ts.hbs')
      },
      {
        type: 'add',
        path: 'src/frontend/react_app/src/components/{{pascalCase name}}/{{pascalCase name}}.test.tsx',
        templateFile: tmpl('react-component/component.test.tsx.hbs')
      }
    ]
  });

  plop.setGenerator('dash-module', {
    description: 'Create a Dash module',
    prompts: [
      { type: 'input', name: 'name', message: 'Module name:' }
    ],
    actions: [
      {
        type: 'add',
        path: 'src/backend/components/{{snakeCase name}}.py',
        templateFile: tmpl('dash-module/module.py.hbs')
      }
    ]
  });
}
