/**
 * Formate une date ISO en format court français (JJ/MM/AAAA HH:MM)
 * @param dateStr (string) : Chaîne de date ISO ou Date
 * @returns (string) : Date formatée
 */
export function formatDateShort(dateStr: string | Date): string {
  const date = typeof dateStr === "string" ? new Date(dateStr) : dateStr;
  return date.toLocaleString('fr-FR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}
