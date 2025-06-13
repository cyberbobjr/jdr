// Mock des dépendances AVANT tout import
// Utiliser une closure pour encapsuler le mock et éviter le hoisting error de Vitest
vi.mock("@/core/api", () => {
  const getActiveSessionsMock = vi.fn();
  return {
    __esModule: true,
    default: {
      getActiveSessions: getActiveSessionsMock,
    },
    getActiveSessionsMock,
  };
});

vi.mock("@/components/CardComponent.vue", () => ({
  default: {
    name: "CardComponent",
    props: ["title"],
    template: `<div class="card">{{ title }}<slot /><slot name="footer" /></div>`,
  },
}));

vi.mock("@/components/JdrSpinner.vue", () => ({
  default: {
    name: "JdrSpinner",
    template: "<div class='spinner'>Chargement...</div>",
  },
}));

import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import SessionsView from "@/views/SessionsView.vue";

// Récupérer le mock via le module mocké
import api from "@/core/api";
const getActiveSessionsMock = vi.mocked(api.getActiveSessions);

describe("SessionsView", () => {
  const mockSessions = [
    {
      session_id: "1",
      scenario_name: "Scénario Test",
      character_name: "Aragorn",
      status: "active" as "active" | "paused" | "completed",
      last_activity: "2024-06-10T12:00:00Z",
    },
    {
      session_id: "2",
      scenario_name: "Aventure 2",
      character_name: "Legolas",
      status: "active" as "active" | "paused" | "completed",
      last_activity: "2024-06-10T13:00:00Z",
    },
  ];

  beforeEach(() => {
    getActiveSessionsMock.mockReset();
    getActiveSessionsMock.mockResolvedValue(mockSessions);
  });

  it("affiche le loader pendant le chargement", async () => {
    // On force le composant à rester en loading
    getActiveSessionsMock.mockImplementation(
      () => new Promise(() => {})
    );
    const wrapper = mount(SessionsView);
    expect(wrapper.html()).toContain("Chargement");
    // Nettoyage du mock pour les autres tests
    getActiveSessionsMock.mockReset();
    getActiveSessionsMock.mockResolvedValue(mockSessions);
  });

  it("affiche la liste des sessions actives", async () => {
    const wrapper = mount(SessionsView);
    await flushPromises();
    expect(wrapper.text()).toContain("Sessions en cours");
    expect(wrapper.text()).toContain("Aragorn");
    expect(wrapper.text()).toContain("Legolas");
    expect(wrapper.findAll(".card").length).toBe(2);
  });

  it("affiche le titre du scénario et le nom du personnage", async () => {
    const wrapper = mount(SessionsView);
    await flushPromises();
    expect(wrapper.text()).toContain("Scénario Test");
    expect(wrapper.text()).toContain("Aventure 2");
    expect(wrapper.text()).toContain("Personnage :");
    expect(wrapper.text()).toContain("Dernière activité :");
  });

  it("déclenche l'action sur le bouton Voir la session", async () => {
    window.alert = vi.fn();
    const wrapper = mount(SessionsView);
    await flushPromises();
    const btns = wrapper.findAll("button.jdr-btn.jdr-btn-primary");
    expect(btns.length).toBe(2);
    await btns[0].trigger("click");
    expect(window.alert).toHaveBeenCalledWith("Session sélectionnée: 1");
  });
});
