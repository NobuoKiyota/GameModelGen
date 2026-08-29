// =============================================================
// Shape Presets Registry
// =============================================================
window.ShapeRegistry = {
  categories: {},
  allConfigs: {},

  registerCategory: function(catKey, catLabel) {
    if (!this.categories[catKey]) {
      this.categories[catKey] = { label: catLabel, shapes: [] };
    }
  },

  registerShape: function(catKey, shapeKey, config) {
    if (!this.categories[catKey]) {
      this.registerCategory(catKey, catKey);
    }
    this.categories[catKey].shapes.push(shapeKey);
    this.allConfigs[shapeKey] = config;
  },

  getConfig: function(shapeKey) {
    return this.allConfigs[shapeKey];
  },

  // Helper to wrap Three.js base geometry into standard raw mesh data
  wrapThreeGeometry: function(geoFunc) {
    return function(p) {
      const geo = geoFunc(p);
      geo.computeVertexNormals();
      const posAttr = geo.getAttribute('position');
      const uvAttr = geo.getAttribute('uv');
      const normAttr = geo.getAttribute('normal');
      const indexAttr = geo.getIndex();

      const positions = Array.from(posAttr.array);
      const uvs = uvAttr ? Array.from(uvAttr.array) : [];
      const normals = normAttr ? Array.from(normAttr.array) : [];
      let indices = [];
      if (indexAttr) indices = Array.from(indexAttr.array);
      else for (let i = 0; i < posAttr.count; i++) indices.push(i);

      return { positions, uvs, normals, indices };
    };
  }
};
