/**
 * Fetch all markets from PNP Exchange
 * Usage: node fetch_markets.js
 */

const { PNPClient } = require('pnp-sdk');

const RPC_URL = process.env.RPC_URL || 'https://api.mainnet-beta.solana.com';

async function main() {
    try {
        // Initialize read-only client
        const client = new PNPClient(RPC_URL);

        // Fetch all markets
        const { count, data } = await client.fetchMarkets();

        // Format output
        const markets = data.map(({ publicKey, account }) => ({
            address: publicKey,
            question: account.question,
            creator: account.creator.toString('hex'),
            endTime: new Date(Number(account.end_time) * 1000).toISOString(),
            resolved: account.resolved,
            resolvable: account.resolvable,
            winningToken: account.winning_token_id || null
        }));

        // Output JSON
        console.log(JSON.stringify({
            success: true,
            count: count,
            markets: markets
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
