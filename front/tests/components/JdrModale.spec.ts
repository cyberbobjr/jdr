import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import JdrModale from "@/components/JdrModale.vue";

describe("JdrModale", () => {
  it("affiche le titre, le sous-titre et le slot", () => {
    const wrapper = mount(JdrModale, {
      props: {
        title: "Titre test",
        subtitle: "Sous-titre test",
        showOk: true,
        showCancel: true,
        okLabel: "Valider",
        cancelLabel: "Annuler",
      },
      slots: {
        default: "<div class='slot-content'>Contenu de la modale</div>",
      },
    });
    expect(wrapper.text()).toContain("Titre test");
    expect(wrapper.text()).toContain("Sous-titre test");
    expect(wrapper.find(".slot-content").exists()).toBe(true);
  });

  it("affiche les boutons ok et cancel avec les bons labels", () => {
    const wrapper = mount(JdrModale, {
      props: {
        title: "Titre",
        showOk: true,
        showCancel: true,
        okLabel: "OK",
        cancelLabel: "Annuler",
      },
    });
    expect(wrapper.find("button.jdr-btn-primary").exists()).toBe(true);
    expect(wrapper.find("button.jdr-btn-primary").text()).toBe("OK");
    expect(wrapper.find("button.jdr-btn-secondary").exists()).toBe(true);
    expect(wrapper.find("button.jdr-btn-secondary").text()).toBe("Annuler");
  });

  it("n'affiche pas les boutons si showOk/showCancel sont false", () => {
    const wrapper = mount(JdrModale, {
      props: {
        title: "Titre",
        showOk: false,
        showCancel: false,
      },
    });
    expect(wrapper.find("button.jdr-btn-primary").exists()).toBe(false);
    expect(wrapper.find("button.jdr-btn-secondary").exists()).toBe(false);
  });

  it("émet 'close' avec true quand on clique sur OK", async () => {
    const wrapper = mount(JdrModale, {
      props: {
        title: "Titre",
        showOk: true,
        okLabel: "OK",
      },
    });
    await wrapper.find("button.jdr-btn-primary").trigger("click");
    expect(wrapper.emitted("close")).toBeTruthy();
    expect(wrapper.emitted("close")![0]).toEqual([true]);
  });

  it("émet 'close' avec false quand on clique sur Cancel", async () => {
    const wrapper = mount(JdrModale, {
      props: {
        title: "Titre",
        showCancel: true,
        cancelLabel: "Annuler",
      },
    });
    await wrapper.find("button.jdr-btn-secondary").trigger("click");
    expect(wrapper.emitted("close")).toBeTruthy();
    expect(wrapper.emitted("close")![0]).toEqual([false]);
  });

  it("ferme la modale si on clique sur le backdrop", async () => {
    const wrapper = mount(JdrModale, {
      props: {
        title: "Titre",
        showCancel: true,
      },
    });
    await wrapper.find(".jdr-modal-backdrop").trigger("click");
    expect(wrapper.emitted("close")).toBeTruthy();
    expect(wrapper.emitted("close")![0]).toEqual([false]);
  });
});
