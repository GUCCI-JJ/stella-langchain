/**
 * 将文件字节大小转换为常见易读的显示格式
 * @param bytes - 字节数（File.size）
 * @param decimals - 保留的小数位数，默认 2
 * @param base - 进制，默认 1024（二进制），传 1000 则使用 SI 单位
 * @returns 格式化后的字符串，如 "1.5 MB"
 */
export function formatFileSize(
  bytes: number,
  decimals: number = 2,
  base: 1024 | 1000 = 1024,
): string {
  // 处理边界情况
  if (!Number.isFinite(bytes) || bytes < 0) return "0 B";
  if (bytes === 0) return "0 B";

  const units =
    base === 1024
      ? ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
      : ["B", "kB", "MB", "GB", "TB", "PB", "EB"];

  const k = base;
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  // 保留小数并去掉末尾多余的 0
  const value = parseFloat((bytes / Math.pow(k, i)).toFixed(decimals));

  return `${value} ${units[i]}`;
}
