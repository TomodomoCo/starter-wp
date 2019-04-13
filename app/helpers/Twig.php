<?php

namespace Tomodomo\Helpers;

use Pimple\Container;
use Psr\Http\Message\ResponseInterface;
use Timber;

class Twig
{
    /**
     * @param Container
     *
     * @return void
     */
    public function __construct(Container $container)
    {
        $this->container = $container;

        return;
    }

    /**
     * Compile a template.
     *
     * @param string|array $template
     * @param array        $context
     *
     * @return string
     */
    public function compile($template, array $context = []) : string
    {
        // Build the context settings
        $settings = array_merge(
            $context,
            $this->container['context']
        );

        // Make sure template an array
        $template = is_array($template) ? $template : [$template];

        return Timber::compile($template, $settings);
    }

    /**
     * Compiles a Twig view, adds it to the PSR7 response body stream,
     * and returns the response. Inspired by Slim Framework's Twig
     * integration: https://github.com/slimphp/Twig-View
     *
     * @param ResponseInterface $response
     * @param string|array      $template
     * @param array             $context
     *
     * @return ResponseInterface
     */
    public function render(ResponseInterface $response, $template, array $context = []) : ResponseInterface
    {
        $response->getBody()->write($this->compile($template, $context));

        return $response;
    }
}
