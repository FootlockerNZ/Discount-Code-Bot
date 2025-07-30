# Swine Codes: Automated Discount Code Fulfilment System

Swine Codes is a fully automated system for distributing discount codes and referral-based account bonuses across a variety of online retailers. The system validates purchases, generates accounts when needed, and delivers fulfilments directly to users via a Discord bot — completely hands-free.

---

## 🎯 Supported Products

- **SNKRDUNK Referral Codes & Accounts**
- **Hype DC 20% Off**
- **Stylerunner 10% Off**
- **Subtype 20% Off**
- **Doordash Accounts**

---

## ⚙️ How It Works

1. **Purchase**: A user makes a purchase through [Swine Codes](https://swinecodes.bgng.io/products).
2. **Validation**: Purchase details (invoice ID and email) are validated against the payment API (`Billgang`).
3. **Referral Input** *(SNKRDUNK only)*: Customers provide their 6-character SNKRDUNK referral code.
4. **Generation**: If the item is an account-based product, temporary emails are used to automate account creation and attach the customer's referral.
5. **Fulfilment**: Codes or accounts are automatically DM'd to the purchaser via the Discord bot.

---

## 🤖 Discord Bot Commands

### `/swine_redeem`
Redeems purchased discount codes (e.g., Hype DC, Subtype, Stylerunner).

**Params:**
- `order_id`: Invoice ID
- `email`: Your purchase email

---

### `/swine_redeem_snkrdunk`
Generates SNKRDUNK accounts using your referral code.

**Params:**
- `order_id`: Invoice ID
- `email`: Purchase email
- `code`: Your SNKRDUNK 6-char referral code

---

### `/swine_admin_add`
Manually trigger SNKRDUNK generation (admin only).

**Params:**
- `code`: SNKRDUNK referral code
- `amount`: Number of accounts to generate

---

### `/swine_shop`
Displays current products and offerings.

---

### `/swine_help` & `/swine_help_snkrdunk`
Provides user guidance on redeeming purchases.

---

### `/swine_get_code`
Fetches verification codes for SNKRDUNK sign-ups via disposable email inbox.

---

## 📦 Features

- **Purchase Validation**: Ensures codes are only sent to verified, paying users.
- **Multi-threaded Generation**: Each SNKRDUNK account is generated in its own thread.
- **Redemption Logging**: Prevents duplicate fulfilment via `completedOrders.txt` and CSV logging.
- **Dynamic Stock Management**: Retrieves and updates stock from local files per product.
- **Temporary Email Integration**: Uses Privatix/RapidAPI to handle throwaway inboxes.

---

## 📁 File Structure

Codes/
├── used.csv # Log of fulfilled items and associated codes
├── snkrdunk.txt # Stockpile of SNKRDUNK referral codes
├── hypedc.txt # Hype DC codes
├── stylerunner.txt # Stylerunner codes
├── subtype.txt # Subtype codes

---

## 🛠 Setup

1. Place your API keys and bot token in `config.json`:
```json
{
  "discordBotToken": "YOUR_TOKEN",
  "billgangAPI": "YOUR_API_KEY",
  "billgangShopId": "YOUR_SHOP_ID",
  "rapidAPI": "YOUR_RAPID_API_KEY",
  "discordSupportUserId": "DISCORD_USER_ID"
}
