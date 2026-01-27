/**
 * Get detailed market information
 * Usage: node get_market_info.js <market_address>
 */

const { PNPClient } = require('pnp-sdk');
const { PublicKey } = require('@solana/web3.js');

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

        // Fetch market data
        const market = new PublicKey(marketAddress);
        const { account } = await client.fetchMarket(market);

        // Format output
        const marketInfo = {
            address: marketAddress,
            question: account.question,
            creator: new PublicKey(account.creator).toBase58(),
            endTime: new Date(Number(account.end_time) * 1000).toISOString(),
            resolved: account.resolved,
            resolvable: account.resolvable,
            winningToken: account.winning_token_id || null,
            yesTokenMint: new PublicKey(account.yes_token_mint).toBase58(),
            noTokenMint: new PublicKey(account.no_token_mint).toBase58(),
            collateralToken: new PublicKey(account.collateral_token).toBase58()
        };

        // Output JSON
        console.log(JSON.stringify({
            success: true,
            market: marketInfo
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
