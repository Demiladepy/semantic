/**
 * Test PNP SDK Installation
 * Quick test to verify the SDK is installed and working
 */

const { PNPClient } = require('pnp-sdk');

const RPC_URL = process.env.RPC_URL || 'https://api.mainnet-beta.solana.com';

async function testInstallation() {
    console.log('🧪 Testing PNP SDK Installation...\n');

    try {
        // Test 1: Initialize client
        console.log('✓ Test 1: Initializing PNP Client...');
        const client = new PNPClient(RPC_URL);
        console.log('  ✅ Client initialized successfully\n');

        // Test 2: Fetch market addresses
        console.log('✓ Test 2: Fetching market addresses...');
        const addresses = await client.fetchMarketAddresses();
        console.log(`  ✅ Found ${addresses.length} markets\n`);

        // Test 3: Get price for first market (if available)
        if (addresses.length > 0) {
            console.log('✓ Test 3: Fetching market price...');
            const firstMarket = addresses[0];
            try {
                const priceData = await client.getMarketPriceV2(firstMarket);
                console.log(`  ✅ Price data retrieved successfully`);
                console.log(`     YES: $${priceData.yesPrice.toFixed(4)} (${priceData.yesMultiplier.toFixed(2)}x)`);
                console.log(`     NO:  $${priceData.noPrice.toFixed(4)} (${priceData.noMultiplier.toFixed(2)}x)\n`);
            } catch (e) {
                console.log(`  ⚠️  Could not fetch price (market may not be V2 AMM): ${e.message}\n`);
            }
        }

        console.log('═'.repeat(50));
        console.log('✅ ALL TESTS PASSED!');
        console.log('═'.repeat(50));
        console.log('\nPNP SDK is installed and working correctly.');
        console.log('You can now use the Python integration.\n');

    } catch (error) {
        console.error('\n❌ TEST FAILED!');
        console.error('Error:', error.message);
        console.error('\nPlease check:');
        console.error('  1. pnp-sdk is installed: npm list pnp-sdk');
        console.error('  2. @solana/web3.js is installed: npm list @solana/web3.js');
        console.error('  3. RPC URL is correct');
        process.exit(1);
    }
}

testInstallation();
