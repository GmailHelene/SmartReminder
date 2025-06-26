// Define focus modes
const focusModes = [
    { name: 'Stillemodus', description: 'Minimizes distractions.' },
    { name: 'ADHD-modus', description: 'Increases focus with engaging tasks.' },
    { name: 'Modus for eldre', description: 'Simplifies interface for easier use.' }
];

// Function to set focus mode
function setFocusMode(modeName) {
    const mode = focusModes.find(m => m.name === modeName);
    if (mode) {
        console.log(`Focus mode set to: ${mode.name}`);
        // Implement additional logic for each mode
    } else {
        console.log('Invalid focus mode selected.');
    }
}

// Example usage
setFocusMode('Stillemodus'); // Set to quiet mode
