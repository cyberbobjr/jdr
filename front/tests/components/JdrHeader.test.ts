import { mount, RouterLinkStub } from "@vue/test-utils";
import JdrHeader from "../../src/components/JdrHeader.vue";

describe("JdrHeader", () => {
  it("affiche le titre et les liens principaux", () => {
    const wrapper = mount(JdrHeader, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
        },
      },
    });
    expect(wrapper.text()).toContain("Terres du Milieu");
    expect(wrapper.text()).toContain("Accueil");
    expect(wrapper.text()).toContain("Sessions");
    expect(wrapper.text()).toContain("Nouvelle Aventure");
    expect(wrapper.text()).toContain("Personnages");
    expect(wrapper.text()).toContain("Scénarios");
  });

  it("ouvre et ferme le menu mobile", async () => {
    // Simule un affichage mobile (768px ou moins)
    window.innerWidth = 500;
    window.dispatchEvent(new Event("resize"));

    const wrapper = mount(JdrHeader, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
        },
      },
    });
    const btn = wrapper.find(".mobile-menu-btn");
    const mobileNav = wrapper.find(".mobile-nav");

    // Au départ, le menu mobile est caché (v-show => display: none)
    expect(mobileNav.attributes("style")).toContain("display: none");

    await btn.trigger("click");
    // Après clic, le menu mobile doit être visible (pas de display: none)
    expect(mobileNav.attributes("style") ?? "").not.toContain("display: none");

    await btn.trigger("click");
    // Après second clic, le menu mobile est à nouveau caché
    expect(mobileNav.attributes("style")).toContain("display: none");
  });
});
