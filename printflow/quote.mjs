/** Standalone educational quotation model. No private Likhora code or data. */
export function quote({width, height, quantity, rush = false, delivery = 0}) {
  for (const [key, value] of Object.entries({width, height, quantity, delivery})) {
    if (typeof value !== 'number' || !Number.isFinite(value)) throw new Error(`${key} must be a finite number`);
  }
  if (width <= 0 || width > 100 || height <= 0 || height > 100) throw new Error('Dimensions must be greater than 0 and at most 100 ft');
  if (!Number.isInteger(quantity) || quantity < 1 || quantity > 1000) throw new Error('Quantity must be a whole number from 1 to 1000');
  if (typeof rush !== 'boolean') throw new Error('Rush must be true or false');
  if (delivery < 0 || delivery > 100000 || Math.abs(delivery * 100 - Math.round(delivery * 100)) > 1e-7) throw new Error('Delivery must be 0–100000 with at most two decimals');
  const areaPerPiece = Math.max(6, width * height);
  const subtotalCents = Math.round(areaPerPiece * 2500) * quantity;
  const rushCents = rush ? Math.round(subtotalCents * .2) : 0;
  const totalCents = subtotalCents + rushCents + Math.round(delivery * 100);
  return {areaPerPiece, subtotalCents, rushCents, totalCents, depositCents: Math.round(totalCents / 2)};
}
