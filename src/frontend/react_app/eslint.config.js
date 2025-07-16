import js from '@eslint/js'
import globals from 'globals'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import eslintImport from 'eslint-plugin-import'
import tseslint from 'typescript-eslint'
import { globalIgnores } from 'eslint/config'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    ignores: ['node_modules/', 'out/'],
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      react.configs.flat.recommended,
      eslintImport.flatConfigs.recommended,
      eslintImport.flatConfigs.typescript,
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
      globals: globals.browser,
    },
    rules: {
      'import/no-restricted-paths': [
        'error',
        {
          zones: [
            { target: './src/features', from: './src/widgets' },
            { target: './src/entities', from: './src/features' },
            { target: './src/entities', from: './src/widgets' },
          ],
        },
      ],
    },
  },
])
