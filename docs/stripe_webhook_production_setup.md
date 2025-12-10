# Stripe Webhook Production Setup

## Problem
The Stripe CLI webhook listener (`stripe listen --forward-to localhost:5000/student/stripe-webhook`) only works for local development. In production (CapRover), Stripe cannot reach your webhook endpoint, so payments appear successful in Stripe but don't update in your database.

## Solution: Configure Production Webhook in Stripe Dashboard

### Step 1: Get Your Production URL
Your webhook endpoint will be:
```
https://your-caprover-domain.com/student/stripe-webhook
```

For example:
- `https://cwmt.your-server.com/student/stripe-webhook`
- `https://app.cwmt.com/student/stripe-webhook`

### Step 2: Add Webhook Endpoint in Stripe Dashboard

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to **Developers** → **Webhooks**
3. Click **"Add endpoint"**
4. Enter your endpoint URL: `https://your-domain.com/student/stripe-webhook`
5. Click **"Select events"**
6. Select these events:
   - `payment_intent.succeeded` (required for successful payments)
   - `payment_intent.payment_failed` (optional for failed payment tracking)
   - `charge.dispute.created` (optional for dispute tracking)
   - `charge.dispute.funds_withdrawn` (optional for dispute tracking)
   - `charge.dispute.closed` (optional for dispute tracking)
7. Click **"Add events"** then **"Add endpoint"**

### Step 3: Get Webhook Signing Secret

1. After creating the endpoint, you'll see it in the webhooks list
2. Click on the endpoint to view details
3. Click **"Reveal"** next to **Signing secret**
4. Copy the secret (starts with `whsec_...`)

### Step 4: Add Secret to CapRover Environment Variables

1. Go to your CapRover dashboard
2. Navigate to your app
3. Go to **App Configs** → **Environmental Variables**
4. Add new variable:
   - **Key**: `STRIPE_WEBHOOK_SECRET`
   - **Value**: `whsec_...` (the signing secret you copied)
5. Save and restart your app

### Step 5: Test the Webhook

1. Make a test payment in your production app
2. Check Stripe Dashboard → Developers → Webhooks → [Your endpoint]
3. You should see webhook attempts listed
4. Check your app logs for:
   ```
   ===== STRIPE WEBHOOK RECEIVED =====
   Event type: payment_intent.succeeded
   Webhook processed successfully
   ===== WEBHOOK PROCESSING COMPLETE =====
   ```

## Troubleshooting

### Webhook Shows "Failed" in Stripe Dashboard

Check these:

1. **Endpoint URL is correct**: Must be exact HTTPS URL including `/student/stripe-webhook`
2. **App is running**: CapRover app must be running and accessible
3. **Environment variable set**: `STRIPE_WEBHOOK_SECRET` must be set in CapRover
4. **Check app logs**: Look for error messages in CapRover logs

### Webhook Signature Verification Fails

- Ensure `STRIPE_WEBHOOK_SECRET` in CapRover matches the secret from Stripe Dashboard
- Make sure you copied the correct secret for the production endpoint (not the test mode secret)
- Verify there are no extra spaces or characters in the environment variable

### Payment Succeeds but Database Not Updated

1. Check if webhook is being received: Look for log entry `===== STRIPE WEBHOOK RECEIVED =====`
2. Check if webhook is processing: Look for `Webhook processed successfully`
3. If not received, verify endpoint URL in Stripe Dashboard
4. If received but failing, check error logs for specific error message

### Testing in Development vs Production

**Development (Local):**
- Use Stripe CLI: `stripe listen --forward-to localhost:5000/student/stripe-webhook`
- Uses temporary webhook secret from CLI output
- Set `STRIPE_WEBHOOK_SECRET` to the CLI secret (starts with `whsec_...`)

**Production (CapRover):**
- Configure webhook endpoint in Stripe Dashboard
- Use permanent webhook secret from dashboard
- Set `STRIPE_WEBHOOK_SECRET` in CapRover environment variables

## Important Notes

1. **You need BOTH**:
   - Local webhook (Stripe CLI) for development
   - Production webhook (Stripe Dashboard) for CapRover

2. **Different secrets**: Development and production have different webhook secrets

3. **Test mode vs Live mode**: 
   - In test mode: Use test webhook endpoint and test secret
   - In live mode: Use live webhook endpoint and live secret

4. **Webhook events are independent**: Even if payment succeeds, database won't update without webhook delivery

## Security Notes

- Never commit webhook secrets to Git
- Keep secrets in environment variables only
- The webhook endpoint (`/student/stripe-webhook`) does NOT require user login (by design)
- Stripe signature verification ensures only Stripe can trigger the webhook
- Without signature verification (no secret), endpoint is insecure

## Verification Checklist

- [ ] Production URL is correct and accessible
- [ ] Webhook endpoint added in Stripe Dashboard
- [ ] Correct events selected (at minimum: `payment_intent.succeeded`)
- [ ] Webhook signing secret copied
- [ ] `STRIPE_WEBHOOK_SECRET` set in CapRover
- [ ] App restarted after adding environment variable
- [ ] Test payment made in production
- [ ] Webhook delivery successful in Stripe Dashboard
- [ ] Payment status updated in database
- [ ] No errors in application logs
