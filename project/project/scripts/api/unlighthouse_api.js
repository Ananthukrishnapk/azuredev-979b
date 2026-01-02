import runUnlighthouse from '../dist/unlighthouse_engine.js'

const urlArg = process.argv[2];
const runIdArg = process.argv[3]; // optional: isolate output folder per run

if (!urlArg) {
    console.error("Error: Please provide a URL.");
    process.exit(1);
}

// Execute the imported function
console.log('Scanning : ', urlArg);
runUnlighthouse(urlArg, runIdArg)
    .then((result) => {
        // console.log(JSON.stringify(result)); // Print JSON so Python can parse it
        process.exit(0);
    })
    .catch((err) => {
        console.error(err);
        process.exit(1);
    });
