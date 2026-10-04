// Synthetic fixture producer only. It does not call a model or a service.
module.exports = class SyntheticSubscriptionProvider {
  id() {
    return 'synthetic-subscription';
  }

  async callApi(_prompt, context) {
    return { output: JSON.stringify(context.vars.observation) };
  }
};
