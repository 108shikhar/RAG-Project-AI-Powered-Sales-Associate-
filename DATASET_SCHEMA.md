# ApnaMart Live Product Catalog Schema (`Dataset/products.json` & `products.csv`)

## 1. Data Source & Web Scraping
- **Target Website:** [ApnaMart Official Store](https://apnamarts.shop/)
- **Brand Slogan:** *"Sab Kuch, Ek Hi Jagah"*
- **Store Location:** Veerpur Vishen, Gonda, Uttar Pradesh - 271310
- **Database Engine:** Supabase PostgreSQL REST API (`https://wjypcfbqacmspcjznlje.supabase.co`)
- **Scraping Methodology:** Direct authenticated REST pagination against public tables `products` and `categories`, capturing live inventory, official Supabase image storage URLs (`https://wjypcfbqacmspcjznlje.supabase.co/storage/v1/object/public/product-images/...`), and local assets.

## 2. Catalog Statistics
- **Total Scraped & Enriched Products:** **103 products**
- **Dense Vector Embeddings:** 768-dimensional dense vectors pre-computed using `sentence-transformers/all-mpnet-base-v2` architecture.
- **Supported Retail Categories (100% Coverage, Zero Failures):**
  1. **Fashion:** 45 products (Men's 3-piece Italian wool suits, 2-piece business suits, cotton casual shirts, wrinkle-free formal shirts, baggy jeans, straight fit denim, kurtas, winter fleece hoodies, lowers/track pants, women's Kanjivaram silk sarees, floral kurtis, executive power blazers, girls' tops, and traditional suit sets)
  2. **Mobiles & Tech:** 11 products (5G Ultra Flagship 256GB/12GB, OnePlus Nord 5G 128GB, Realme 5G, Samsung Galaxy M-series, Budget 4G phones, 65W GaN dual-port chargers, 33W fast chargers, 20,000mAh dual-USB power banks, shockproof liquid silicone covers)
  3. **Electronics & Audio:** 10 products (Over-ear wireless headphones 45h ANC, Sony style extra bass headphones, boAt ANC true wireless earbuds, Noise ColorFit AMOLED calling smartwatch, Fire-Boltt voice smartwatch, boAt Stone 14W rugged speaker, JBL waterproof 20W speaker, HP 14-inch thin & light laptop)
  4. **Beauty & Grooming:** 9 products (Lakme 9to5 matte liquid lipstick 3-pack, 12-piece professional makeup brush kit, Garnier vitamin C face serum, Derma Co hyaluronic sunscreen SPF 50, Biotique anti-hairfall shampoo, men's 5-in-1 waterproof beard trimmer, Philips rotary shaver, Fogg luxury EDP perfume)
  5. **Sports & Fitness:** 8 products (Asian cushioned EVA air running shoes, breathable mesh running sneakers, Nivia official size 5 rubber football, official size 7 basketball, Yonex carbon badminton racket set with shuttles, Strauss willow cricket bat, Kore 20kg PVC home gym dumbbells, Boldfit 6mm anti-skid yoga mat)
  6. **Toys & Kids:** 7 products (Smartivity STEM hydraulic crane building toy, 120-piece interlocking building blocks, 4WD 360-degree stunt RC racing car, Hot Wheels 5-car collector pack, friction pull-back cars 4-pack, wooden handcrafted chess set, 3-feet giant plush cuddle teddy bear)
  7. **Home & Kitchen:** 7 products (Prestige 5-piece non-stick granite cookware set with glass lids, 5-piece stainless steel induction cookware set, Hawkins Contura 3L hard anodized pressure cooker, Butterfly Hero 750W heavy duty 3-jar mixer grinder, Milton 1.8L fast boil electric kettle, Milton 1000ml thermosteel insulated bottle, 6-piece airtight storage jar set)
  8. **Grocery & Staples:** 6 products (Premium aged long-grain basmati rice 5kg, Aashirvaad 100% shudh chakki whole wheat atta 10kg, Fortune Sunlite refined sunflower oil 5L, Kacchi Ghani pure mustard oil 1L, Tata Tea Gold aromatic Assam tea 1kg, Nutraj California raw almonds & whole cashews combo 1kg, Tata Sampann unpolished toor dal 1kg)

## 3. JSON Field Schema
| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `id` | `string` | Unique product identifier | `"APNAMART-CAT-085"` |
| `name` | `string` | Full descriptive product title | `"Raymond Style Italian Wool 3-Piece Full Suit"` |
| `category` | `string` | Main retail department | `"Fashion"` |
| `sub_category` | `string` | Specific sub-department | `"Men"` |
| `type` | `string` | Exact commodity type | `"Suit"` |
| `price` | `integer` | Current selling price in ₹ INR | `3499` |
| `original_price` | `integer` | Maximum Retail Price (MRP in ₹) | `7999` |
| `discount` | `string` | Percentage discount | `"56% OFF"` |
| `rating` | `float` | Customer satisfaction rating (out of 5.0) | `4.9` |
| `reviews_count`| `integer` | Number of verified customer reviews | `840` |
| `inStock` | `boolean` | Inventory availability | `true` |
| `image` | `string` | Verified CDN / Supabase image URL | `"https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=500"` |
| `occasion` | `array[str]` | Suitable usage occasions | `["Office Wear", "Interview", "Wedding"]` |
| `sizes` | `array[str]` | Available sizes or storage/pack specs | `["S", "M", "L", "XL", "XXL"]` |
| `colors` | `array[str]` | Available colorways | `["Navy Blue", "Charcoal Black"]` |
| `description` | `string` | Comprehensive product specifications | `"Tailored 3-piece formal suit including notched-lapel..."` |
| `tags` | `array[str]` | Search indexing tokens | `["fashion", "men", "suit", "office wear"]` |
| `embedding` | `array[float]`| 768-D L2-normalized vector | `[0.0241, -0.0152, ..., 0.0489]` (768 numbers) |
