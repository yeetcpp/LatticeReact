const fs = require('fs');
const path = require('path');

const componentsDir = 'frontend-react/src/components';

const files = fs.readdirSync(componentsDir)
  .filter(f => f.endsWith('.tsx'))
  .map(f => path.join(componentsDir, f));

let replacements = 0;

for (const file of files) {
  let content = fs.readFileSync(file, 'utf8');
  let originalContent = content;

  // Navigation
  if (file.endsWith('Navigation.tsx')) {
    content = content.replace(/className="bg-gradient-to-br from-\[\#adc6ff\] to-\[\#4d8eff\].*?"/g, 'className="btn-primary"');
  }

  // Hero Section
  if (file.endsWith('HeroSection.tsx')) {
    content = content.replace(/className="bg-gradient-to-br from-\[\#adc6ff\] to-\[\#4d8eff\].*?"/g, 'className="btn-primary-lg"');
    content = content.replace(/className="glass border border-\[\#424754\]\/30.*?transition-colors"/g, 'className="btn-secondary-lg"');
  }

  // Chat Interface
  if (file.endsWith('ChatInterface.tsx')) {
    content = content.replace(/className="p-2 glass-morphism.*?transition-colors"/g, 'className="btn-icon"');
    content = content.replace(/className="px-3 py-1 text-xs glass-morphism rounded-full hover:bg-white\/20 transition-colors"/g, 'className="btn-ghost text-xs"');
    content = content.replace(/className="px-6 py-3 bg-gradient-to-r from-accent-purple to-accent-teal rounded-lg font-medium.*?"/g, 'className="btn-primary"');
    content = content.replace(/bg-primary\/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white\/20/g, 'glass-card');
  }

  // Chat Section
  if (file.endsWith('ChatSection.tsx')) {
    content = content.replace(/className="bg-gradient-to-br from-\[\#adc6ff\] to-\[\#4d8eff\].*?"/g, 'className="btn-primary"');
    content = content.replace(/className="p-3 bg-\[\#2a2a3c\]\/50 hover:bg-\[\#2a2a3c\] border.*?"/g, 'className="btn-icon"');
    content = content.replace(/className="p-3 glass rounded-xl border border-\[\#424754\]\/30.*?"/g, 'className="btn-icon"');
  }

  if (content !== originalContent) {
    fs.writeFileSync(file, content);
    console.log(`Updated ${file}`);
    replacements++;
  }
}
console.log(`Done. ${replacements} files updated.`);
