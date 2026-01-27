/**
 * Redeem winning position in a resolved market
 * Usage: node redeem_position.js <market_address>
 */

const { PNPClient } = require('pnp-sdk');
const { PublicKey } = require('@solana/web3.js');

const RPC_URL = process.env.RPC_URL || 'https://api.mainnet-beta.solana.com';
const PRIVATE_KEY = process.env.PNP_PRIVATE_KEY;

const marketAddress = process.argv[2];

async function main() {
    if (!marketAddress) {
        console.error(JSON.stringify({
            success: false,
            error: 'Market address required'
        }));
        process.exit(1);
    }

    if (!PRIVATE_KEY) {
        console.error(JSON.stringify({
            success: false,
            error: 'PNP_PRIVATE_KEY environment variable required'
        }));
        process.exit(1);
    }

    try {
        // Initialize client with private key
        const secretKey = PNPClient.parseSecretKey(PRIVATE_KEY);
        const client = new PNPClient(RPC_URL, secretKey);

        const market = new PublicKey(marketAddress);

        // Check if market is resolved
        const { account } = await client.fetchMarket(market);

        if (!account.resolved) {
            throw new Error('Market is not yet resolved');
        }

        // Redeem position
        const result = await client.redeemPosition(market);

        // Output JSON
        console.log(JSON.stringify({
            success: true,
            redemption: {
                signature: result.signature,
                winningToken: account.winning_token_id
            }
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
