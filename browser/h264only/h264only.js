(function () {
  const blocked = /(vp0?8|vp0?9|av01|av1)/i;
  const wrap = (obj, name) => { const orig = obj[name]; if (!orig) return;
    obj[name] = function (type) { if (typeof type === 'string' && blocked.test(type)) return name === 'canPlayType' ? '' : false; return orig.apply(this, arguments); }; };
  wrap(window.MediaSource || {}, 'isTypeSupported');
  wrap(HTMLMediaElement.prototype, 'canPlayType');
  if (window.MediaCapabilities && MediaCapabilities.prototype.decodingInfo) {
    const orig = MediaCapabilities.prototype.decodingInfo;
    MediaCapabilities.prototype.decodingInfo = function (config) {
      const codec = config && ((config.video && config.video.contentType) || '');
      if (blocked.test(codec)) return Promise.resolve({ supported: false, smooth: false, powerEfficient: false });
      return orig.apply(this, arguments);
    };
  }
})();
