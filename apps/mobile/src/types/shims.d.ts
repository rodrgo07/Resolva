declare module "react-native" {
  export const View: any;
  export const Text: any;
  export const StyleSheet: any;
  export const ScrollView: any;
  export const TouchableOpacity: any;
  export const TextInput: any;
  export const ActivityIndicator: any;
  export const Alert: any;
  export const FlatList: any;
  export const Modal: any;
  export const SafeAreaView: any;
  export const KeyboardAvoidingView: any;
  export const Platform: any;
}
declare module "zustand" {
  export interface StoreHook<T> {
    (): T;
    getState: () => T;
    setState: (partial: Partial<T> | ((state: T) => Partial<T>)) => void;
  }
  export const create: <T>(initializer: (set: any, get: any) => T) => StoreHook<T>;
}
