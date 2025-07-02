#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const [, , ...args] = process.argv;
const title = args.join(' ').trim();
if (!title) {
  console.error('Usage: npm run adr:new "Title"');
  process.exit(1);
}

const adrDir = path.join(__dirname, '..', 'docs', 'adr');
const templatePath = path.join(adrDir, 'template.md');

function slugify(str) {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function nextNumber() {
  if (!fs.existsSync(adrDir)) {
    return '0001';
  }
  const files = fs.readdirSync(adrDir).filter(f => /^\d+-.*\.md$/.test(f));
  const numbers = files.map(f => parseInt(f.split('-')[0], 10));
  const max = numbers.length ? Math.max(...numbers) : 0;
  return String(max + 1).padStart(4, '0');
}

const number = nextNumber();
const slug = slugify(title);
const date = new Date().toISOString().slice(0, 10);

let content = fs.readFileSync(templatePath, 'utf8');
content = content
  .replace(/{{NUMBER}}/g, number)
  .replace(/{{TITLE}}/g, title)
  .replace(/{{DATE}}/g, date);

const target = path.join(adrDir, `${number}-${slug}.md`);
fs.writeFileSync(target, content);
console.log(`ADR created: ${target}`);
