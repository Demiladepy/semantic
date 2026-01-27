/**
 * Get market price data for a V2 AMM market
 * Usage: node get_market_price.js <market_address>
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

        // Get market price data
        const priceData = await client.getMarketPriceV2(marketAddress);

        // Output JSON
        console.log(JSON.stringify({
            success: true,
            priceData: priceData
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
