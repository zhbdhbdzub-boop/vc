// Service for module purchase in frontend
import api from '../lib/api';

export interface ModulePurchaseRequest {
  module_id: string;
  license_type: 'trial' | 'monthly' | 'annual' | 'lifetime';
  payment_method_id?: string;
}

export interface ModulePurchaseResponse {
  message: string;
  license: any;
  charge_id?: string;
}

class ModulePurchaseService {
  /**
   * Start a trial for a module
   */
  async startTrial(moduleId: string): Promise<ModulePurchaseResponse> {
    const response = await api.post(`/api/modules/marketplace/${moduleId}/purchase/`, {
      license_type: 'trial'
    });
    return response.data;
  }

  /**
   * Purchase a module with payment
   */
  async purchaseModule(
    moduleId: string,
    licenseType: 'monthly' | 'annual' | 'lifetime',
    paymentMethodId: string
  ): Promise<ModulePurchaseResponse> {
    const response = await api.post(`/api/modules/marketplace/${moduleId}/purchase/`, {
      license_type: licenseType,
      payment_method_id: paymentMethodId
    });
    return response.data;
  }

  /**
   * Check if user has access to a module
   */
  async checkAccess(moduleCode: string): Promise<boolean> {
    try {
      const response = await api.get('/api/my-modules/');
      const licenses = response.data;
      return licenses.some((license: any) => 
        license.module.code === moduleCode && license.is_active
      );
    } catch (error) {
      return false;
    }
  }
}

export const modulePurchaseService = new ModulePurchaseService();
