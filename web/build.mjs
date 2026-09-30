import {mkdir, readFile, writeFile, copyFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
const root = fileURLToPath(new URL('.', import.meta.url));
await mkdir(join(root, 'dist'), {recursive: true});
const hashes = {};
for (const file of ['index.html', 'style.css', 'app.mjs', 'model.mjs']) {
  if (file.endsWith('.mjs')) execFileSync(process.execPath, ['--check', join(root, file)]);
  hashes[file] = createHash('sha256').update(await readFile(join(root, file))).digest('hex');
  await copyFile(join(root, file), join(root, 'dist', file));
}
await writeFile(join(root, 'dist', 'manifest.json'), JSON.stringify(hashes, null, 2) + '\n');
console.log('C3 production assets built and syntax checked.');
