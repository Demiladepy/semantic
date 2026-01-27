/**
 * Get settlement criteria from proxy server
 * Usage: node get_settlement_criteria.js <market_address>
 */

const { PNPClient } = require('pnp-sdk');

const RPC_URL = process.env.RPC_URL || 'https://api.mainnet-beta.solana.com';
const marketAddress = process.argv[2];

async function main() {
    if (!marketAddress) {
        console.error(JSON.stringify({
            success: false,
            error: 'Market address required'
        }));
        process.exit(1);
    }

    try {
        // Initialize read-only client
        const client = new PNPClient(RPC_URL);

        // Fetch settlement criteria
        const criteria = await client.fetchSettlementCriteria(marketAddress);

        // Output JSON
        console.log(JSON.stringify({
            success: true,
            criteria: criteria
        }));

    } catch (error) {
        console.error(JSON.stringify({
            success: false,
            error: error.message
        }));
        process.exit(1);
    }
}

main();
