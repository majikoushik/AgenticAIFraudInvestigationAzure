import { entraConfig } from "@/auth/authConfig";
import { PublicClientApplication } from "@azure/msal-browser";

export const msalConfig = {
  auth: {
    clientId: entraConfig.clientId,
    authority: entraConfig.authority,
    redirectUri: entraConfig.redirectUri
  }
};

export const msalInstance = new PublicClientApplication(msalConfig);
