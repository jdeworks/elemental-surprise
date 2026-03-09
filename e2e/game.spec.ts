import { test, expect, type Page, type Locator } from '@playwright/test';

async function dragElement(page: Page, fromLocator: Locator, toLocator: Locator) {
  const fromBox = await fromLocator.boundingBox();
  const toBox = await toLocator.boundingBox();
  
  if (!fromBox || !toBox) return;
  
  await page.mouse.move(fromBox.x + fromBox.width / 2, fromBox.y + fromBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(toBox.x + toBox.width / 2, toBox.y + toBox.height / 2, { steps: 10 });
  await page.mouse.up();
}

test.describe('Element Merge Game', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('library shows 4 starter elements', async ({ page }) => {
    await expect(page.locator('[data-testid="library"]')).toBeVisible();
    await expect(page.locator('[data-testid="library-element-fire"]')).toBeVisible();
    await expect(page.locator('[data-testid="library-element-water"]')).toBeVisible();
    await expect(page.locator('[data-testid="library-element-earth"]')).toBeVisible();
    await expect(page.locator('[data-testid="library-element-wind"]')).toBeVisible();
  });

  test('spawns element when library item clicked', async ({ page }) => {
    await page.click('[data-testid="library-element-fire"]');
    await expect(page.locator('[data-testid="workspace"]')).toContainText('Fire');
  });

  test('fire + water = steam', async ({ page }) => {
    await page.click('[data-testid="library-element-fire"]');
    await page.click('[data-testid="library-element-water"]');

    const fire = page.locator('[data-testid="element-fire"]').first();
    const water = page.locator('[data-testid="element-water"]').first();

    await dragElement(page, fire, water);

    await expect(page.locator('[data-testid="element-steam"]')).toBeVisible();
    await expect(page.locator('[data-testid="element-fire"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="element-water"]')).not.toBeVisible();
  });

  test('earth + fire = lava', async ({ page }) => {
    await page.click('[data-testid="library-element-earth"]');
    await page.click('[data-testid="library-element-fire"]');

    const earth = page.locator('[data-testid="element-earth"]').first();
    const fire = page.locator('[data-testid="element-fire"]').first();

    await dragElement(page, earth, fire);

    await expect(page.locator('[data-testid="element-lava"]')).toBeVisible();
  });

  test('earth + wind = dust', async ({ page }) => {
    await page.click('[data-testid="library-element-earth"]');
    await page.click('[data-testid="library-element-wind"]');

    const earth = page.locator('[data-testid="element-earth"]').first();
    const wind = page.locator('[data-testid="element-wind"]').first();

    await dragElement(page, earth, wind);

    await expect(page.locator('[data-testid="element-dust"]')).toBeVisible();
  });

  test('fire + wind = energy', async ({ page }) => {
    await page.click('[data-testid="library-element-fire"]');
    await page.click('[data-testid="library-element-wind"]');

    const fire = page.locator('[data-testid="element-fire"]').first();
    const wind = page.locator('[data-testid="element-wind"]').first();

    await dragElement(page, fire, wind);

    await expect(page.locator('[data-testid="element-energy"]')).toBeVisible();
  });

  test('earth + water = mud', async ({ page }) => {
    await page.click('[data-testid="library-element-earth"]');
    await page.click('[data-testid="library-element-water"]');

    const earth = page.locator('[data-testid="element-earth"]').first();
    const water = page.locator('[data-testid="element-water"]').first();

    await dragElement(page, earth, water);

    await expect(page.locator('[data-testid="element-mud"]')).toBeVisible();
  });

  test('water + wind = rain', async ({ page }) => {
    await page.click('[data-testid="library-element-water"]');
    await page.click('[data-testid="library-element-wind"]');

    const water = page.locator('[data-testid="element-water"]').first();
    const wind = page.locator('[data-testid="element-wind"]').first();

    await dragElement(page, water, wind);

    await expect(page.locator('[data-testid="element-rain"]')).toBeVisible();
  });

  test('persists discovered elements after refresh', async ({ page }) => {
    await page.click('[data-testid="library-element-fire"]');
    await page.click('[data-testid="library-element-water"]');

    const fire = page.locator('[data-testid="element-fire"]').first();
    const water = page.locator('[data-testid="element-water"]').first();

    await dragElement(page, fire, water);

    await expect(page.locator('[data-testid="element-steam"]')).toBeVisible();

    await page.reload();

    await expect(page.locator('[data-testid="library-element-steam"]')).toBeVisible();
  });

  test('localStorage is obfuscated', async ({ page }) => {
    await page.click('[data-testid="library-element-fire"]');

    const storageValue = await page.evaluate(() => {
      return localStorage.getItem('element-merge-game');
    });

    expect(storageValue).not.toBeNull();
    expect(storageValue).not.toContain('fire');
    expect(storageValue).not.toContain('{"discovered"');
  });
});
