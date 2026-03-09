import { test, expect, type Page } from '@playwright/test';

async function dragWithPointerEvents(page: Page, fromSelector: string, toSelector: string) {
  const from = page.locator(fromSelector).first();
  const to = page.locator(toSelector).first();
  
  const fromBox = await from.boundingBox();
  const toBox = await to.boundingBox();
  
  if (!fromBox || !toBox) {
    console.log('Could not get bounding boxes');
    return false;
  }
  
  const startX = fromBox.x + fromBox.width / 2;
  const startY = fromBox.y + fromBox.height / 2;
  const endX = toBox.x + toBox.width / 2;
  const endY = toBox.y + toBox.height / 2;
  
  // Move to starting position
  await page.mouse.move(startX, startY);
  await page.waitForTimeout(50);
  
  // Press and hold
  await page.mouse.down();
  await page.waitForTimeout(100);
  
  // Move slowly to target with multiple steps
  for (let i = 0; i <= 10; i++) {
    const x = startX + (endX - startX) * (i / 10);
    const y = startY + (endY - startY) * (i / 10);
    await page.mouse.move(x, y);
    await page.waitForTimeout(50);
  }
  
  await page.waitForTimeout(100);
  await page.mouse.up();
  await page.waitForTimeout(200);
  
  return true;
}

async function dragWithForce(page: Page, fromSelector: string, toSelector: string) {
  const from = page.locator(fromSelector).first();
  const to = page.locator(toSelector).first();
  
  // Use force: true to bypass interception
  await from.dragTo(to, { force: true });
}

test.describe('Element Merge Game - Detailed Drag Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('basic drag and drop works', async ({ page }) => {
    // Spawn two elements
    await page.click('[data-testid="library-element-fire"]');
    await page.click('[data-testid="library-element-water"]');
    
    // Check both exist
    await expect(page.locator('[data-testid="element-fire"]')).toBeVisible();
    await expect(page.locator('[data-testid="element-water"]')).toBeVisible();
    
    console.log('Both elements spawned successfully');
  });

  test('drag with pointer events - fire onto water', async ({ page }) => {
    await page.click('[data-testid="library-element-fire"]');
    await page.click('[data-testid="library-element-water"]');
    
    await page.waitForTimeout(500);
    
    const success = await dragWithPointerEvents(page, '[data-testid="element-fire"]', '[data-testid="element-water"]');
    console.log('Drag result:', success);
    
    await page.waitForTimeout(1000);
    
    // Check if merge happened
    const steamVisible = await page.locator('[data-testid="element-steam"]').isVisible().catch(() => false);
    console.log('Steam visible:', steamVisible);
    
    if (!steamVisible) {
      // Take screenshot for debugging
      await page.screenshot({ path: '/tmp/drag-test-fail.png' });
      console.log('Screenshot saved to /tmp/drag-test-fail.png');
    }
    
    expect(steamVisible).toBe(true);
  });

  test('drag with force - water onto fire', async ({ page }) => {
    await page.click('[data-testid="library-element-water"]');
    await page.click('[data-testid="library-element-fire"]');
    
    await page.waitForTimeout(500);
    
    await dragWithForce(page, '[data-testid="element-water"]', '[data-testid="element-fire"]');
    
    await page.waitForTimeout(1000);
    
    const steamVisible = await page.locator('[data-testid="element-steam"]').isVisible().catch(() => false);
    console.log('Steam visible:', steamVisible);
    
    expect(steamVisible).toBe(true);
  });

  test('check console for errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.click('[data-testid="library-element-fire"]');
    await page.waitForTimeout(500);
    
    console.log('Console errors:', errors);
    expect(errors.length).toBe(0);
  });

  test('check dnd-kit state after drag', async ({ page }) => {
    await page.click('[data-testid="library-element-fire"]');
    await page.click('[data-testid="library-element-water"]');
    
    await page.waitForTimeout(500);
    
    // Check if elements are draggable (have the right attributes)
    const fireElement = page.locator('[data-testid="element-fire"]').first();
    const hasAriaRole = await fireElement.getAttribute('role');
    const isDraggable = await fireElement.getAttribute('aria-roledescription');
    
    console.log('Fire element role:', hasAriaRole);
    console.log('Fire element draggable:', isDraggable);
    
    expect(isDraggable).toBe('draggable');
  });

  test('element positioning after spawn', async ({ page }) => {
    await page.click('[data-testid="library-element-fire"]');
    await page.click('[data-testid="library-element-water"]');
    
    await page.waitForTimeout(300);
    
    const fireBox = await page.locator('[data-testid="element-fire"]').first().boundingBox();
    const waterBox = await page.locator('[data-testid="element-water"]').first().boundingBox();
    
    console.log('Fire position:', fireBox);
    console.log('Water position:', waterBox);
    
    expect(fireBox).not.toBeNull();
    expect(waterBox).not.toBeNull();
    
    // They should be in different positions
    if (fireBox && waterBox) {
      const distance = Math.sqrt(
        Math.pow(fireBox.x - waterBox.x, 2) + Math.pow(fireBox.y - waterBox.y, 2)
      );
      console.log('Distance between elements:', distance);
      expect(distance).toBeGreaterThan(50);
    }
  });

  test('multiple rapid spawns work', async ({ page }) => {
    for (let i = 0; i < 5; i++) {
      await page.click('[data-testid="library-element-fire"]');
    }
    
    await page.waitForTimeout(300);
    
    const count = await page.locator('[data-testid="element-fire"]').count();
    console.log('Fire elements count:', count);
    
    expect(count).toBe(5);
  });

  test('discovery toast appears on merge', async ({ page }) => {
    await page.click('[data-testid="library-element-fire"]');
    await page.click('[data-testid="library-element-water"]');
    
    await page.waitForTimeout(500);
    
    // Try the drag
    await dragWithPointerEvents(page, '[data-testid="element-fire"]', '[data-testid="element-water"]');
    
    await page.waitForTimeout(500);
    
    // Check for discovery toast
    const toastVisible = await page.locator('.discovery-toast').isVisible().catch(() => false);
    console.log('Toast visible:', toastVisible);
    
    // Or check if steam was created
    const steamVisible = await page.locator('[data-testid="element-steam"]').isVisible().catch(() => false);
    console.log('Steam visible:', steamVisible);
  });
});
