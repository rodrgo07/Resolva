import { useState, useEffect } from "react";
import { 
  Smartphone, QrCode, Trash2, CheckCircle2,
  Clock, Edit3, Plus, Laptop
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { formatDate } from "@/lib/utils";

interface Device {
  id: number;
  device_id: string;
  device_name: string;
  platform: string;
  app_version: string;
  status: string;
  is_trusted: boolean;
  last_seen_at: string;
  paired_at: string;
}

interface PairingStartResponse {
  pairing_code: string;
  qr_payload: string;
  nonce: string;
  expires_at: string;
  server_endpoint: string;
  desktop_device_id: string;
}

export function DeviceSettingsTab() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isPairingModalOpen, setIsPairingModalOpen] = useState(false);
  const [pairingData, setPairingData] = useState<PairingStartResponse | null>(null);
  const [isStartingPair, setIsStartingPair] = useState(false);
  const [editingDeviceId, setEditingDeviceId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const { toast } = useToast();

  const loadDevices = async () => {
    try {
      const list = await api.get<Device[]>("/api/devices");
      setDevices(list || []);
    } catch {
      toast({ title: "Erro ao carregar dispositivos", type: "error" });
    }
  };

  useEffect(() => {
    loadDevices();
  }, []);

  const handleStartPairing = async () => {
    setIsStartingPair(true);
    try {
      const res = await api.post<PairingStartResponse>("/api/devices/pair/start");
      setPairingData(res);
      setIsPairingModalOpen(true);
    } catch {
      toast({ title: "Erro ao gerar código de pareamento", type: "error" });
    } finally {
      setIsStartingPair(false);
    }
  };

  const handleRevokeDevice = async (deviceId: string) => {
    if (!confirm("Deseja realmente revogar o acesso deste dispositivo? O Mobile perderá acesso imediatamente.")) return;
    try {
      await api.post(`/api/devices/${deviceId}/revoke`);
      toast({ title: "Dispositivo revogado com sucesso", type: "success" });
      await loadDevices();
    } catch {
      toast({ title: "Erro ao revogar dispositivo", type: "error" });
    }
  };

  const handleRenameDevice = async (deviceId: string) => {
    if (!editName.trim()) return;
    try {
      await api.patch(`/api/devices/${deviceId}`, { device_name: editName.trim() });
      toast({ title: "Dispositivo renomeado", type: "success" });
      setEditingDeviceId(null);
      await loadDevices();
    } catch {
      toast({ title: "Erro ao renomear dispositivo", type: "error" });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header com botão de Pareamento */}
      <div className="glass-card p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Smartphone className="w-4 h-4 text-accent-400" />
              Dispositivos Conectados (RESOLVA Mobile)
            </h3>
            <p className="text-xs text-surface-400 mt-0.5">
              Gerencie celulares Android e iOS pareados com seu RESOLVA Desktop através da Sync Layer segura.
            </p>
          </div>

          <Button
            type="button"
            size="sm"
            onClick={handleStartPairing}
            isLoading={isStartingPair}
            className="gap-2 text-xs"
          >
            <Plus className="w-3.5 h-3.5" />
            Conectar Novo Celular
          </Button>
        </div>

        {/* Modal / Card de Pareamento */}
        {isPairingModalOpen && pairingData && (
          <div className="p-4 rounded-xl border border-accent-500/30 bg-accent-500/5 space-y-3 mt-4 animate-fade-in">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-accent-300 uppercase tracking-wider flex items-center gap-1.5">
                <QrCode className="w-4 h-4 text-accent-400" /> Handshake de Pareamento Seguro
              </span>
              <button 
                onClick={() => setIsPairingModalOpen(false)}
                className="text-xs text-surface-400 hover:text-white"
              >
                ✕ Fechar
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center">
              <div className="space-y-2">
                <p className="text-xs text-surface-300 leading-relaxed">
                  1. Abra o app <strong>RESOLVA Mobile</strong> no seu celular.<br/>
                  2. Toque em <strong>"Conectar ao RESOLVA"</strong>.<br/>
                  3. Digite o código de uso único abaixo ou escaneie a sessão:
                </p>
                <div className="p-3 bg-surface-900 border border-surface-700 rounded-lg text-center font-mono font-bold text-xl text-accent-400 tracking-widest">
                  {pairingData.pairing_code.slice(0, 3)} {pairingData.pairing_code.slice(3)}
                </div>
                <p className="text-[11px] text-surface-500 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> Expira em 5 minutos • Uso único
                </p>
              </div>

              <div className="p-3 bg-surface-900/60 border border-surface-800 rounded-lg text-xs space-y-1.5 font-mono text-surface-400">
                <div><strong className="text-white">Desktop ID:</strong> {pairingData.desktop_device_id}</div>
                <div><strong className="text-white">Endpoint Local:</strong> {pairingData.server_endpoint}</div>
                <div className="truncate"><strong className="text-white">Nonce:</strong> {pairingData.nonce}</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Lista de Dispositivos */}
      <div className="glass-card p-5 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Laptop className="w-4 h-4 text-emerald-400" />
          Dispositivos Pareados Ativos
        </h3>

        {devices.length === 0 ? (
          <div className="p-6 text-center text-xs text-surface-500 border border-surface-800 rounded-lg">
            Nenhum smartphone pareado até o momento. Clique em "Conectar Novo Celular" para iniciar.
          </div>
        ) : (
          <div className="space-y-3">
            {devices.map((d) => (
              <div
                key={d.id}
                className="p-4 rounded-xl border border-surface-800 bg-surface-900/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {editingDeviceId === d.device_id ? (
                      <div className="flex items-center gap-1.5">
                        <input
                          type="text"
                          value={editName}
                          onChange={(e) => setEditName(e.target.value)}
                          className="px-2 py-0.5 bg-surface-800 border border-surface-700 text-white rounded text-xs"
                        />
                        <Button size="sm" onClick={() => handleRenameDevice(d.device_id)} className="h-6 px-2 text-[10px]">
                          Salvar
                        </Button>
                      </div>
                    ) : (
                      <>
                        <span className="font-bold text-white text-sm">{d.device_name}</span>
                        <button 
                          onClick={() => { setEditingDeviceId(d.device_id); setEditName(d.device_name); }}
                          className="text-surface-400 hover:text-white"
                        >
                          <Edit3 className="w-3 h-3" />
                        </button>
                      </>
                    )}
                    <Badge variant="outline" className="text-[10px] uppercase font-mono">
                      {d.platform} • v{d.app_version}
                    </Badge>
                  </div>
                  <p className="text-surface-500 font-mono text-[11px]">
                    ID: {d.device_id} • Pareado em: {formatDate(d.paired_at)}
                  </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                    <CheckCircle2 className="w-3 h-3" /> Conectado
                  </span>
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    onClick={() => handleRevokeDevice(d.device_id)}
                    className="h-7 px-2.5 text-xs gap-1"
                  >
                    <Trash2 className="w-3 h-3" />
                    Revogar
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
