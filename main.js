const { bigNumbersUF } = require('./scripts/bigNumbersUF.js');
const { SEFetcher } = require('./scripts/SEFetcher.js');
const { semanaEpidemiologica } = require('./scripts/semanaEpidemiologica.js');
const { cityCases } = require('./scripts/cityCases.js');


const startTime = new Date();
console.log(`[INFO] Start: ${startTime.getHours()}:${startTime.getMinutes().toString().padStart(2, '0')}\n`);

async function main() {
    try {
        // console.log('\n=== Running semanaEpidemiologica ===\n');
        // await semanaEpidemiologica();
        // console.log('\n=== semanaEpidemiologica completed ===\n');

        // console.log('\n=== Running bigNumbersUF ===\n');
        // await bigNumbersUF();
        // console.log('\n=== bigNumbersUF completed ===\n');

        // console.log('\n=== Running SEFetcher ===\n');
        // await SEFetcher();
        // console.log('\n=== SEFetcher completed ===\n');

         console.log('\n=== Running cityCases ===\n');
         await cityCases();
         console.log('\n=== cityCases completed ===\n');

    } catch (error) {
        console.error(`[ERROR] An error occurred: ${error.message}`);
    } finally {
        const endTime = new Date();
        console.log(`\n[INFO] End: ${endTime.getHours()}:${endTime.getMinutes().toString().padStart(2, '0')}`);
    }
}

main();