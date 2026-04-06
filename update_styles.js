const fs = require('fs');
const content = fs.readFileSync('frontend-react/src/index.css', 'utf8');

const buttonStyles = `
@layer base {
  button {
    @apply inline-flex items-center justify-center font-space font-medium rounded-xl transition-all duration-300 ease-in-out cursor-pointer active:scale-95 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-50;
  }
}

@layer components {
  /* Override styles on specific button configurations */
  .btn-primary {
    @apply bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold py-3 px-6 hover:from-purple-500 hover:to-indigo-500 border border-transparent shadow-[0_0_15px_rgba(167,139,250,0.4)] hover:shadow-[0_0_25px_rgba(167,139,250,0.6)];
  }
  .btn-secondary {
    @apply bg-white/5 hover:bg-white/10 text-white border border-white/10 backdrop-blur-md py-3 px-6 shadow-sm hover:shadow-md;
  }
  .btn-icon {
    @apply p-2 rounded-full hover:bg-white/10 transition-colors;
  }
}
`;

const updatedContent = content.replace('@tailwind utilities;', '@tailwind utilities;\n' + buttonStyles);
fs.writeFileSync('frontend-react/src/index.css', updatedContent);

