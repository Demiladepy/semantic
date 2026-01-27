/**
 * Fetch market addresses from proxy server
 * Usage: node fetch_market_addresses.js
 */

const { PNPClient } = require('pnp-sdk');

const RPC_URL = process.env.RPC_URL || 'https://api.mainnet-beta.solana.com';

async function main() {
    try {
        // Initialize read-only client
        const client = new PNPClient(RPC_URL);

        // Fetch market addresses from proxy
        const addresses = await client.fetchMarketAddresses();

        // Output JSON
        console.log(JSON.stringify({
            success: true,
            count: addresses.length,
            addresses: addresses
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
