/**
 * Buy tokens in a PNP market
 * Usage: node buy_tokens.js <market_address> <YES|NO> <amount_base_units>
 */

const { PNPClient } = require('pnp-sdk');
const { PublicKey } = require('@solana/web3.js');

const RPC_URL = process.env.RPC_URL || 'https://api.mainnet-beta.solana.com';
const PRIVATE_KEY = process.env.PNP_PRIVATE_KEY;

const marketAddress = process.argv[2];
const side = process.argv[3];
const amountBase = process.argv[4];

async function main() {
    if (!marketAddress || !side || !amountBase) {
        console.error(JSON.stringify({
            success: false,
            error: 'Usage: node buy_tokens.js <market_address> <YES|NO> <amount_base_units>'
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

        if (!client.trading) {
            throw new Error('Trading module not available');
        }

        const market = new PublicKey(marketAddress);
        const buyYesToken = side.toUpperCase() === 'YES';
        const amount = parseFloat(amountBase) / 1_000_000; // Convert to USDC

        // Execute trade
        const result = await client.trading.buyTokensUsdc({
            market: market,
            buyYesToken: buyYesToken,
            amountUsdc: amount
        });

        // Output JSON
        console.log(JSON.stringify({
            success: true,
            trade: {
                signature: result.signature,
                tokensReceived: result.tokensReceived || 'N/A',
                side: side.toUpperCase()
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
