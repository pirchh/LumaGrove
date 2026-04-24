import { authFetch } from './auth';
import type { Asset } from './content';

export async function uploadAdminAsset(file: File): Promise<Asset> {
  const body = new FormData();
  body.append('file', file);

  const response = await authFetch('/admin/assets/upload', {
    method: 'POST',
    body,
    // Deliberately do not set Content-Type. Browser sets multipart boundary.
  });

  if (!response.ok) {
    throw new Error(`Asset upload failed: ${response.status}`);
  }

  return response.json();
}
