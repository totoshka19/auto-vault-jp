// Фиксированный курс: 1 JPY = 0.6 RUB
export const JPY_TO_RUB = 0.6;

export function yenToRub(yen: number): number {
  return Math.round(yen * JPY_TO_RUB);
}

export function rubToYen(rub: number): number {
  return Math.round(rub / JPY_TO_RUB);
}

export function formatRub(amount: number): string {
  return amount.toLocaleString('ru-RU') + ' ₽';
}
