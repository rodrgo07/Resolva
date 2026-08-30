import { create } from "zustand";
import type { Notification, NotificationSummary } from "@/types";
import { api } from "@/lib/api-client";

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  summary: NotificationSummary | null;
  isOpen: boolean;

  setNotifications: (notifications: Notification[]) => void;
  setSummary: (summary: NotificationSummary) => void;
  addNotification: (notification: Notification) => void;
  markAsRead: (id: number) => void;
  dismissNotification: (id: number) => void;
  markAllAsRead: () => void;
  setOpen: (open: boolean) => void;
  toggleOpen: () => void;
  fetchSummary: () => Promise<void>;
  fetchNotifications: () => Promise<void>;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  summary: null,
  isOpen: false,

  setNotifications: (notifications) =>
    set({
      notifications,
      unreadCount: notifications.filter((n) => !n.is_read).length,
    }),

  setSummary: (summary) =>
    set({
      summary,
      unreadCount: summary.unread_count,
    }),

  addNotification: (notification) =>
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + (notification.is_read ? 0 : 1),
    })),

  markAsRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  dismissNotification: (id) =>
    set((state) => {
      const target = state.notifications.find((n) => n.id === id);
      const wasUnread = target && !target.is_read;
      return {
        notifications: state.notifications.filter((n) => n.id !== id),
        unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
      };
    }),

  markAllAsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({
        ...n,
        is_read: true,
        read_at: n.read_at || new Date().toISOString(),
      })),
      unreadCount: 0,
    })),

  setOpen: (open) => set({ isOpen: open }),
  toggleOpen: () => set((s) => ({ isOpen: !s.isOpen })),

  fetchSummary: async () => {
    try {
      const summary = await api.get<NotificationSummary>("/api/notifications/summary");
      if (summary) {
        set({ summary, unreadCount: summary.unread_count });
      }
    } catch {}
  },

  fetchNotifications: async () => {
    try {
      const notifs = await api.get<Notification[]>("/api/notifications/");
      if (notifs) {
        get().setNotifications(notifs);
      }
    } catch {}
  }
}));
