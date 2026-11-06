const API_BASE = window.location.origin;

// State management
const state = {
  cart: [],
  selectedCategory: '',
  selectedSubCategory: '',
  selectedProductType: '',
  selectedOccasionSpec: '',
  selectedSizePurpose: '',
  finalComments: '',
  isProcessing: false
};

// DOM Elements
const mitrLauncherBtn = document.getElementById('mitrLauncherBtn');
const shopsyChatWindow = document.getElementById('shopsyChatWindow');
const closeChatWinBtn = document.getElementById('closeChatWinBtn');
const restartFlowBtn = document.getElementById('restartFlowBtn');
const chatMessagesStream = document.getElementById('chatMessagesStream');

// Dropdown Elements
const selectCategory = document.getElementById('selectCategory');
const groupSubCategory = document.getElementById('groupSubCategory');
const selectSubCategory = document.getElementById('selectSubCategory');
const groupProductType = document.getElementById('groupProductType');
const selectProductType = document.getElementById('selectProductType');
const groupOccasionSpec = document.getElementById('groupOccasionSpec');
const labelOccasionSpec = document.getElementById('labelOccasionSpec');
const selectOccasionSpec = document.getElementById('selectOccasionSpec');
const groupSizePurpose = document.getElementById('groupSizePurpose');
const labelSizePurpose = document.getElementById('labelSizePurpose');
const selectSizePurpose = document.getElementById('selectSizePurpose');
const groupFinalComments = document.getElementById('groupFinalComments');
const inputFinalComments = document.getElementById('inputFinalComments');
const btnSubmitMitrChain = document.getElementById('btnSubmitMitrChain');

// Pipeline Step Nodes
const stepNodes = [
  document.getElementById('stepNode1'),
  document.getElementById('stepNode2'),
  document.getElementById('stepNode3'),
  document.getElementById('stepNode4'),
  document.getElementById('stepNode5')
];

// Modals
const apiSettingsModal = document.getElementById('apiSettingsModal');
const apiConfigTrigger = document.getElementById('apiConfigTrigger');
const closeApiSettingsBtn = document.getElementById('closeApiSettingsBtn');
const apiConfigForm = document.getElementById('apiConfigForm');
const cfgGroqApiKey = document.getElementById('cfgGroqApiKey');
const cfgGroqModel = document.getElementById('cfgGroqModel');
const cfgHfToken = document.getElementById('cfgHfToken');

const shoppingBagModal = document.getElementById('shoppingBagModal');
const openHeaderCartBtn = document.getElementById('openHeaderCartBtn');
const closeBagBtn = document.getElementById('closeBagBtn');
const cartBadgeCount = document.getElementById('cartBadgeCount');
const cartModalItemsList = document.getElementById('cartModalItemsList');
const bagTotalDisplay = document.getElementById('bagTotalDisplay');
const btnBagCheckout = document.getElementById('btnBagCheckout');
const freeformChatForm = document.getElementById('freeformChatForm');
const freeformInput = document.getElementById('freeformInput');

// ================= COMPREHENSIVE TAXONOMY COVERING ALL 8 APNAMART CATEGORIES =================
const APNAMART_TAXONOMY = {
  "Fashion": {
    subcategories: {
      "Men": {
        types: ["Suit", "Shirt", "Jeans", "T-Shirt", "Lower / Track Pant", "Hoodie"],
        occasions: ["Office Wear", "Interview", "Wedding", "Festive", "Daily Wear"],
        sizes: ["S", "M", "L", "XL", "XXL"],
        specLabel: "Occasion",
        sizeLabel: "Size"
      },
      "Women": {
        types: ["Saree", "Kurti", "Top", "Suit / Blazer Set"],
        occasions: ["Wedding", "Festive", "Office Wear", "Daily Wear", "Party"],
        sizes: ["Free Size", "S", "M", "L", "XL"],
        specLabel: "Occasion",
        sizeLabel: "Size"
      },
      "Kids": {
        types: ["Girl's Top", "Girl's Traditional Suit", "Casuals"],
        occasions: ["Festive", "Birthday Party", "Casual Outing"],
        sizes: ["4-5 Yrs", "6-7 Yrs", "8-9 Yrs", "10-12 Yrs"],
        specLabel: "Occasion",
        sizeLabel: "Age Bracket"
      }
    }
  },
  "Mobiles": {
    subcategories: {
      "Smartphones": {
        types: ["5G Flagship", "5G Smartphone", "Budget Smartphone"],
        occasions: ["256GB Storage", "128GB Storage", "64GB Storage"],
        sizes: ["Daily Use", "Gaming", "Photography"],
        specLabel: "Storage Capacity",
        sizeLabel: "Primary Purpose"
      },
      "Accessories": {
        types: ["Fast Charger", "Mobile Back Cover", "Charging Cable"],
        occasions: ["33W Fast Charging", "Shockproof Protection", "Type-C Braided"],
        sizes: ["Daily Travel", "Office", "Home"],
        specLabel: "Key Spec",
        sizeLabel: "Usage Context"
      }
    }
  },
  "Electronics": {
    subcategories: {
      "Audio": {
        types: ["Wireless Bluetooth Headphones", "Portable Bluetooth Speaker", "True Wireless Earbuds"],
        occasions: ["40h Playback & Deep Bass", "10W Splashproof", "Active Noise Cancellation"],
        sizes: ["Daily Commute", "Gym & Workout", "Party & Home Leisure"],
        specLabel: "Audio Spec",
        sizeLabel: "Primary Use"
      },
      "Wearables": {
        types: ["Smart Fitness Watch", "Calling Smartwatch"],
        occasions: ["Bluetooth Calling", "SpO2 & Heart Rate", "Sports Tracking"],
        sizes: ["Daily Office", "Fitness Tracking", "Casual"],
        specLabel: "Key Feature",
        sizeLabel: "Lifestyle"
      }
    }
  },
  "Beauty": {
    subcategories: {
      "Makeup": {
        types: ["Matte Lipstick Combo", "Makeup Brush Kit (12 pcs)"],
        occasions: ["Office Wear", "Party & Bridal", "Daily Glam"],
        sizes: ["Set of 3 (Everyday Shades)", "12-Piece Set with Pouch"],
        specLabel: "Occasion",
        sizeLabel: "Pack Size"
      },
      "Men Shaving": {
        types: ["Trimmer", "Clean Shave Shaver"],
        occasions: ["Daily Beard Styling", "Clean Shave", "Body Grooming"],
        sizes: ["Complete 5-in-1 Kit", "Single Cordless Trimmer"],
        specLabel: "Grooming Style",
        sizeLabel: "Kit Type"
      }
    }
  },
  "Sports": {
    subcategories: {
      "Footwear": {
        types: ["Men's Running Shoes"],
        occasions: ["Running & Jogging", "Gym & Workout", "Morning Walk"],
        sizes: ["UK 7", "UK 8", "UK 9", "UK 10"],
        specLabel: "Activity",
        sizeLabel: "Footwear Size"
      },
      "Gear": {
        types: ["Basketball Size 7", "Badminton Racket Set", "Home Gym Dumbbells"],
        occasions: ["Outdoor Play", "Tournament & Practice", "Strength Training"],
        sizes: ["Size 7 (Official)", "Standard Adult Set", "10kg-20kg"],
        specLabel: "Level of Play",
        sizeLabel: "Specification"
      }
    }
  },
  "Toys": {
    subcategories: {
      "Educational": {
        types: ["Building Blocks STEM Toy", "Learning Puzzle"],
        occasions: ["Creative Learning", "Birthday Gift", "Indoor Play"],
        sizes: ["120-Piece Kit", "Standard Board"],
        specLabel: "Occasion",
        sizeLabel: "Box Size"
      },
      "Vehicles": {
        types: ["Friction Pull-Back Toy Cars"],
        occasions: ["Toddler Play", "Birthday Return Gift"],
        sizes: ["Pack of 4 Cars"],
        specLabel: "Occasion",
        sizeLabel: "Quantity"
      }
    }
  },
  "Home & Kitchen": {
    subcategories: {
      "Cookware": {
        types: ["Stainless Steel Cookware Set", "Fast Boil Electric Kettle"],
        occasions: ["Daily Cooking", "Kitchen Upgrade", "Festive Meals"],
        sizes: ["5-Piece Induction Set", "1.8L Kettle"],
        specLabel: "Use Case",
        sizeLabel: "Capacity"
      },
      "Storage": {
        types: ["Airtight Storage Jar Set"],
        occasions: ["Kitchen Organizing", "Food Storage"],
        sizes: ["Set of 6 (1000ml each)"],
        specLabel: "Purpose",
        sizeLabel: "Pack Size"
      }
    }
  },
  "Grocery": {
    subcategories: {
      "Staples": {
        types: ["Premium Basmati Rice", "Organic Whole Wheat Atta", "Pure Mustard Oil"],
        occasions: ["Biryani & Daily Meals", "Everyday Cooking", "Healthy Diet"],
        sizes: ["5kg Pack", "10kg Bag", "1L Pouch"],
        specLabel: "Cooking Requirement",
        sizeLabel: "Weight / Volume"
      }
    }
  }
};

// ================= INITIALIZATION =================
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  loadConfig();
});

function setupEventListeners() {
  // Toggle ApnaMart Sahayak Window
  mitrLauncherBtn.addEventListener('click', () => {
    shopsyChatWindow.classList.toggle('open');
  });
  closeChatWinBtn.addEventListener('click', () => {
    shopsyChatWindow.classList.remove('open');
  });

  // Restart Flow
  restartFlowBtn.addEventListener('click', resetDropdownWizard);

  // 1. Category Dropdown Changed
  selectCategory.addEventListener('change', () => {
    const cat = selectCategory.value;
    state.selectedCategory = cat;
    highlightStepNode(0);

    hideStep(groupSubCategory);
    hideStep(groupProductType);
    hideStep(groupOccasionSpec);
    hideStep(groupSizePurpose);
    hideStep(groupFinalComments);

    if (cat && APNAMART_TAXONOMY[cat]) {
      populateSelect(selectSubCategory, Object.keys(APNAMART_TAXONOMY[cat].subcategories));
      showStep(groupSubCategory);
      highlightStepNode(1);
    }
  });

  // 2. Subcategory Dropdown Changed
  selectSubCategory.addEventListener('change', () => {
    const sub = selectSubCategory.value;
    state.selectedSubCategory = sub;

    hideStep(groupProductType);
    hideStep(groupOccasionSpec);
    hideStep(groupSizePurpose);
    hideStep(groupFinalComments);

    const subData = APNAMART_TAXONOMY[state.selectedCategory]?.subcategories[sub];
    if (subData) {
      populateSelect(selectProductType, subData.types);
      showStep(groupProductType);
      highlightStepNode(2);
    }
  });

  // 3. Product Type Dropdown Changed
  selectProductType.addEventListener('change', () => {
    const pType = selectProductType.value;
    state.selectedProductType = pType;

    hideStep(groupOccasionSpec);
    hideStep(groupSizePurpose);
    hideStep(groupFinalComments);

    const subData = APNAMART_TAXONOMY[state.selectedCategory]?.subcategories[state.selectedSubCategory];
    if (subData) {
      labelOccasionSpec.innerHTML = `<i class="fa-solid fa-calendar-check"></i> 4. Select ${subData.specLabel}:`;
      populateSelect(selectOccasionSpec, subData.occasions);
      showStep(groupOccasionSpec);
      highlightStepNode(3);
    }
  });

  // 4. Occasion / Spec Dropdown Changed
  selectOccasionSpec.addEventListener('change', () => {
    const occ = selectOccasionSpec.value;
    state.selectedOccasionSpec = occ;

    hideStep(groupSizePurpose);
    hideStep(groupFinalComments);

    const subData = APNAMART_TAXONOMY[state.selectedCategory]?.subcategories[state.selectedSubCategory];
    if (subData) {
      labelSizePurpose.innerHTML = `<i class="fa-solid fa-ruler"></i> 5. Select ${subData.sizeLabel}:`;
      populateSelect(selectSizePurpose, subData.sizes);
      showStep(groupSizePurpose);
    }
  });

  // 5. Size / Purpose Dropdown Changed
  selectSizePurpose.addEventListener('change', () => {
    state.selectedSizePurpose = selectSizePurpose.value;
    if (state.selectedSizePurpose) {
      showStep(groupFinalComments);
      highlightStepNode(4);
    }
  });

  // 6. Submit Wizard Chain
  btnSubmitMitrChain.addEventListener('click', handleDropdownWizardSubmit);

  // Freeform Chat Form
  freeformChatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = freeformInput.value.trim();
    if (!query) return;
    freeformInput.value = '';
    executeApnaMartQuery(query, {});
  });

  // Modals
  apiConfigTrigger.addEventListener('click', () => apiSettingsModal.classList.add('open'));
  closeApiSettingsBtn.addEventListener('click', () => apiSettingsModal.classList.remove('open'));
  openHeaderCartBtn.addEventListener('click', openBagModal);
  closeBagBtn.addEventListener('click', () => shoppingBagModal.classList.remove('open'));

  btnBagCheckout.addEventListener('click', () => {
    if (state.cart.length === 0) {
      showToast('Your ApnaMart bag is empty!');
      return;
    }
    state.cart = [];
    updateBagUI();
    shoppingBagModal.classList.remove('open');
    showToast('🎉 ApnaMart Order Placed! Thank you for shopping with ApnaMart (Sab Kuch, Ek Hi Jagah).');
  });
}

function showStep(el) { el.classList.remove('hidden'); }
function hideStep(el) { el.classList.add('hidden'); }

function populateSelect(selectEl, optionsArray) {
  selectEl.innerHTML = '<option value="">-- Choose Option --</option>';
  optionsArray.forEach(opt => {
    const optEl = document.createElement('option');
    optEl.value = opt;
    optEl.textContent = opt;
    selectEl.appendChild(optEl);
  });
}

function highlightStepNode(index) {
  stepNodes.forEach((node, idx) => {
    if (idx <= index) node.classList.add('active');
    else node.classList.remove('active');
  });
}

function resetDropdownWizard() {
  selectCategory.value = '';
  hideStep(groupSubCategory);
  hideStep(groupProductType);
  hideStep(groupOccasionSpec);
  hideStep(groupSizePurpose);
  hideStep(groupFinalComments);
  inputFinalComments.value = '';
  highlightStepNode(-1);
  showToast('ApnaMart Sahayak wizard reset.');
}

// ================= CHAIN EXECUTION =================
async function handleDropdownWizardSubmit() {
  if (state.isProcessing) return;

  const comments = inputFinalComments.value.trim();
  state.finalComments = comments;

  let compositeQuery = `I want ${state.selectedProductType} in ${state.selectedSubCategory} ${state.selectedCategory} for ${state.selectedOccasionSpec}`;
  if (state.selectedSizePurpose) compositeQuery += `, spec: ${state.selectedSizePurpose}`;
  if (comments) compositeQuery += `. Additional preference: ${comments}`;

  const attributesPayload = {
    category: state.selectedCategory,
    sub_category: state.selectedSubCategory,
    type: state.selectedProductType,
    occasion: state.selectedOccasionSpec,
    size: state.selectedSizePurpose,
    comments: comments
  };

  await executeApnaMartQuery(compositeQuery, attributesPayload);
}

async function executeApnaMartQuery(queryText, attributes) {
  state.isProcessing = true;

  appendBubble('user', queryText);
  const typingIndicator = appendTypingBubble();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: queryText,
        category: attributes.category || null,
        sub_category: attributes.sub_category || null,
        attributes: attributes,
        top_k: 5
      })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    typingIndicator.remove();

    appendBubble('mitr', data.sales_pitch);

    if (data.query_sentence) {
      appendSynthesizedBanner(data.query_sentence);
    }

    if (data.top_products && data.top_products.length > 0) {
      appendProductCards(data.top_products);
    }

  } catch (err) {
    console.error('ApnaMart pipeline error:', err);
    typingIndicator.remove();
    appendBubble('mitr', "Maaf kijiye, processing me dikkat aayi. Please check API settings or try again.");
  } finally {
    state.isProcessing = false;
  }
}

function appendBubble(sender, text) {
  const bubble = document.createElement('div');
  bubble.className = sender === 'user' ? 'user-bubble' : 'mitr-bubble';

  let formatted = escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p style="margin-top: 0.4rem;">')
    .replace(/\n- (.*?)/g, '<li style="margin-left: 1rem;">$1</li>');

  bubble.innerHTML = `<p>${formatted}</p>`;
  chatMessagesStream.appendChild(bubble);
  chatMessagesStream.scrollTop = chatMessagesStream.scrollHeight;
  return bubble;
}

function appendTypingBubble() {
  const bubble = document.createElement('div');
  bubble.className = 'mitr-bubble';
  bubble.innerHTML = `
    <div style="display: flex; align-items: center; gap: 0.5rem; color: #94a3b8; font-size: 0.78rem;">
      <i class="fa-solid fa-spinner fa-spin" style="color: #34d399;"></i>
      <span>ApnaMart Sahayak is consulting LangGraph StateGraph &amp; embeddings...</span>
    </div>
  `;
  chatMessagesStream.appendChild(bubble);
  chatMessagesStream.scrollTop = chatMessagesStream.scrollHeight;
  return bubble;
}

function appendSynthesizedBanner(sentence) {
  const banner = document.createElement('div');
  banner.style.cssText = 'background: #090d16; border-left: 3px solid #10b981; border-radius: 6px; padding: 0.55rem 0.75rem; font-size: 0.75rem; font-family: var(--font-mono); color: #cbd5e1;';
  banner.innerHTML = `
    <strong style="color: #34d399; font-size: 0.7rem; display: block; margin-bottom: 0.2rem;"><i class="fa-solid fa-microchip"></i> LangGraph Synthesized Query:</strong>
    "${escapeHtml(sentence)}"
  `;
  chatMessagesStream.appendChild(banner);
  chatMessagesStream.scrollTop = chatMessagesStream.scrollHeight;
}

function appendProductCards(products) {
  const listContainer = document.createElement('div');
  listContainer.className = 'mitr-products-list';

  products.slice(0, 5).forEach((p, idx) => {
    const card = document.createElement('div');
    card.className = 'mitr-product-card';
    const matchPct = Math.round(p.similarity_score * 100);

    card.innerHTML = `
      <img src="${p.image}" alt="${escapeHtml(p.name)}" class="mitr-prod-thumb" onerror="this.src='https://apnamarts.shop/placeholder.svg'" />
      <div class="mitr-prod-details">
        <h5 class="mitr-prod-title">${idx + 1}. ${escapeHtml(p.name)}</h5>
        <div class="mitr-prod-pricing">
          <span>₹${p.price.toLocaleString('en-IN')}</span>
          <span class="disc">${p.discount || 'Great Deal'}</span>
        </div>
        <button class="btn-quick-add" data-id="${p.id}">
          <i class="fa-solid fa-cart-plus"></i> Add to Bag
        </button>
      </div>
      <span class="mitr-prod-match"><i class="fa-solid fa-bullseye"></i> ${matchPct}% Match</span>
    `;

    card.querySelector('.btn-quick-add').addEventListener('click', () => {
      addToCart(p);
    });

    listContainer.appendChild(card);
  });

  chatMessagesStream.appendChild(listContainer);
  chatMessagesStream.scrollTop = chatMessagesStream.scrollHeight;
}

// Cart & Bag
function addToCart(product) {
  state.cart.push(product);
  updateBagUI();
  showToast(`Added "${product.name}" to ApnaMart Bag!`);
}

function updateBagUI() {
  cartBadgeCount.textContent = state.cart.length;
}

function openBagModal() {
  cartModalItemsList.innerHTML = '';
  if (state.cart.length === 0) {
    cartModalItemsList.innerHTML = '<p style="text-align: center; color: #94a3b8; padding: 1.5rem;">Your ApnaMart Bag is empty.</p>';
    bagTotalDisplay.textContent = '₹0';
  } else {
    let sum = 0;
    state.cart.forEach((item, idx) => {
      sum += item.price;
      const row = document.createElement('div');
      row.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.08);';
      row.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <img src="${item.image}" style="width: 36px; height: 36px; border-radius: 4px; object-fit: cover;" onerror="this.src='https://apnamarts.shop/placeholder.svg'" />
          <div>
            <div style="font-size: 0.78rem; font-weight: 600;">${escapeHtml(item.name)}</div>
            <div style="font-size: 0.72rem; color: #10b981; font-weight: 700;">₹${item.price.toLocaleString('en-IN')}</div>
          </div>
        </div>
        <button style="background: none; border: none; color: #ef4444; cursor: pointer;" data-remove="${idx}"><i class="fa-solid fa-trash"></i></button>
      `;
      row.querySelector('[data-remove]').addEventListener('click', () => {
        state.cart.splice(idx, 1);
        updateBagUI();
        openBagModal();
      });
      cartModalItemsList.appendChild(row);
    });
    bagTotalDisplay.textContent = `₹${sum.toLocaleString('en-IN')}`;
  }
  shoppingBagModal.classList.add('open');
}

// API Config
async function loadConfig() {
  try {
    const res = await fetch(`${API_BASE}/api/config`);
    if (res.ok) {
      const data = await res.json();
      if (data.groq_model && cfgGroqModel) cfgGroqModel.value = data.groq_model;
    }
  } catch (e) { console.warn('Config load:', e); }
}

apiConfigForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {};
  if (cfgGroqApiKey.value.trim()) payload.groq_api_key = cfgGroqApiKey.value.trim();
  if (cfgGroqModel.value) payload.groq_model = cfgGroqModel.value;
  if (cfgHfToken.value.trim()) payload.huggingface_api_key = cfgHfToken.value.trim();

  try {
    const res = await fetch(`${API_BASE}/api/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      showToast('Settings saved successfully!');
      apiSettingsModal.classList.remove('open');
    }
  } catch (err) { showToast('Error saving settings'); }
});

function showToast(msg) {
  const container = document.getElementById('shopsyToastContainer');
  const t = document.createElement('div');
  t.className = 'toast-msg';
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
