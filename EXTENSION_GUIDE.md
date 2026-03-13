# Extending Elemental Surprise

## Adding New Elements

### 1. Choose the Appropriate Group
Select the group that best matches your element's nature:
- Technology: Computers, gadgets, digital concepts
- Culture: Arts, entertainment, media, sports
- Society: People, relationships, organizations, government
- Science: Scientific concepts, discoveries, natural phenomena
- AI: Artificial intelligence, machine learning, robotics
- Knowledge: Information, education, language, mathematics
- Materials: Substances, materials, chemicals, elements
- Nature: Natural environments, weather, geological features
- Tools: Instruments, devices, implements
- Food: Edible items, beverages, cooking
- Animals: Living creatures, fauna
- Life: Biological concepts, health, vitality
- Space: Astronomy, cosmos, celestial bodies
- Fantasy: Mythical creatures, magic, supernatural
- Humanity: Human conditions, emotions, experiences
- Other: Miscellaneous items that don't fit elsewhere

### 2. Add the Element
Place your element in the appropriate group bucket:

**Example: Adding "Blockchain" (Technology group)**
1. Find the least-full bucket in `public/data/elements/by-group/technology/` 
   (or create a new one like `technology-bucket-17.json`)
2. Add your element:
   ```json
   {
     "blockchain": {
       "id": "blockchain",
       "name": "Blockchain",
       "icon": "./icons/blockchain.svg",
       "links": [
         {
           "url": "https://en.wikipedia.org/wiki/Blockchain",
           "label": "Wikipedia"
         }
       ],
       "group": "Technology"
     }
   }
   ```

### 3. Update Indices (Optional)
The system will automatically pick up new elements on next load, but for immediate recognition:
- Add to `public/data/elements/index.json`:
  ```json
  {
    "buckets": {
      // ... existing buckets
      "technology-bucket-17": "technology-bucket-17.json"
    },
    "elementToBucket": {
      // ... existing mappings
      "blockchain": "technology-bucket-17"
    }
  }
  ```

## Adding New Recipes

### 1. Determine Input Groups
Identify which groups your input elements belong to:
- Example: `blockchain` (Technology) + `money` (Society) 
- Group combination: "Technology-Society"

### 2. Add the Recipe
Place your recipe in the appropriate group combination directory:

**Example: Adding blockchain + money → cryptocurrency**
1. Navigate to `public/data/recipes/by-group-combination/technology-society/`
2. Find the least-full bucket or create new one
3. Add your recipe:
   ```json
   {
     "blockchain+money": {
       "result": "cryptocurrency",
       "reasoning": "Blockchain technology applied to money creates cryptocurrency"
     }
   }
   ```

### 3. Update Indices (Optional)
For immediate recognition:
- Add to `public/data/recipes/index.json`:
  ```json
  {
    "buckets": {
      // ... existing buckets
      "technology-society-bucket-5": "technology-society-bucket-5.json"
    },
    "recipeKeyToBucket": {
      // ... existing mappings
      "blockchain+money": "technology-society-bucket-5"
    }
  }
  ```

## Naming Conventions

### Element IDs
- Use lowercase with hyphens: `blockchain`, `artificial-intelligence`
- Be descriptive but concise
- Check existing elements for similar naming patterns

### Recipe Keys
- Format: `element1+element2` (alphabetical order)
- Example: `blockchain+money` (not `money+blockchain`)
- The system automatically sorts inputs, but use alphabetical for consistency

### Icons
- Place SVG icons in `public/icons/`
- Use descriptive names: `blockchain.svg`, `cryptocurrency.svg`
- Reference as: `"./icons/your-icon.svg"`

### Reasoning
- Provide clear, logical explanations
- Can be scientific, philosophical, mythological, or humorous
- Match the tone of existing recipes in the game

## Best Practices

### For Elements
1. Always specify a `group` property
2. Include Wikipedia link when applicable
3. Follow existing naming conventions in your group
4. Consider which real-world category the element belongs to

### For Recipes
1. Explain WHY the combination makes sense
2. Consider cross-group combinations for interesting discoveries
3. Within-group combinations can represent specialization/advancement
4. Avoid duplicating existing recipes (check first)
5. Aim for 2-5 new recipes per element to maintain balance

### Validation
Before submitting, verify:
1. Element groups are correct
2. Recipe reasoning is clear and appropriate
3. No duplicate element IDs or recipe keys
4. Files are valid JSON
5. Icons exist and are referenced correctly

## Example Extension Workflow

**Adding "Photosynthesis" element and recipes:**

1. **Element**: Photosynthesis (Life group)
   ```json
   {
     "photosynthesis": {
       "id": "photosynthesis",
       "name": "Photosynthesis",
       "icon": "./icons/photosynthesis.svg",
       "links": [{ "url": "https://en.wikipedia.org/wiki/Photosynthesis", "label": "Wikipedia" }],
       "group": "Life"
     }
   }
   ```

2. **Recipes**:
   ```json
   {
     "plant+sunlight": {
       "result": "photosynthesis",
       "reasoning": "Plants using sunlight to create energy through photosynthesis"
     },
     "chlorophyll+light": {
       "result": "photosynthesis", 
       "reasoning": "Chlorophyll capturing light energy enables photosynthesis"
     },
     "water+carbon-dioxide+sunlight": {
       "result": "photosynthesis",
       "reasoning": "Water, CO2, and sunlight combine in photosynthesis to produce glucose and oxygen"
     }
   }
   ```

This gives players multiple discovery paths to an important biological concept!

## Maintenance Tips

- Periodically run the combination generator to add recipes for underrepresented elements
- Monitor group distributions for balance
- Review new additions for quality and consistency
- Keep backups before major changes